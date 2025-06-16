"""Simple ARXML merge utility with basic conflict resolution."""

import xml.etree.ElementTree as ET
import argparse
import sys


def parse_arxml(path: str) -> ET.ElementTree | None:
    """Parse an ARXML file and return ElementTree or None on failure."""
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        print(f"Failed to parse {path}: {exc}", file=sys.stderr)
        return None
    return tree


def _ns(tag: str) -> str:
    """Return a tag name with namespace stripped."""
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def merge_packages(base_pkg: ET.Element, new_pkg: ET.Element, strategy: str) -> None:
    """Merge two AR-PACKAGES elements in-place."""
    base_map = {
        pkg.findtext("SHORT-NAME"): pkg
        for pkg in base_pkg.findall("AR-PACKAGE")
    }

    for pkg in new_pkg.findall("AR-PACKAGE"):
        name = pkg.findtext("SHORT-NAME")
        if name in base_map:
            if strategy == "latest-wins":
                base_pkg.remove(base_map[name])
                base_pkg.append(pkg)
        else:
            base_pkg.append(pkg)


def merge_trees(trees: list[ET.ElementTree], strategy: str) -> ET.ElementTree:
    """Merge multiple AUTOSAR trees by AR-PACKAGES."""
    base_tree = trees[0]
    base_root = base_tree.getroot()

    ns = base_root.tag.split("}")[0].strip("{") if "}" in base_root.tag else ""

    def find_packages(root: ET.Element) -> ET.Element | None:
        tag = f"{{{ns}}}AR-PACKAGES" if ns else "AR-PACKAGES"
        return root.find(tag)

    base_pkgs = find_packages(base_root)

    for t in trees[1:]:
        root = t.getroot()
        pkgs = find_packages(root)
        if pkgs is None:
            continue
        if base_pkgs is None:
            base_root.append(pkgs)
            base_pkgs = pkgs
        else:
            merge_packages(base_pkgs, pkgs, strategy)

    return base_tree


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Merge multiple AUTOSAR ARXML files into a single output file.")
    parser.add_argument("output", help="Path to output ARXML file")
    parser.add_argument("inputs", nargs="+", help="Input ARXML files")
    parser.add_argument(
        "--strategy",
        choices=["conservative", "latest-wins"],
        default="conservative",
        help="Conflict resolution strategy (default: conservative)",
    )
    args = parser.parse_args(argv)

    trees: list[ET.ElementTree] = []
    for path in args.inputs:
        tree = parse_arxml(path)
        if tree is not None:
            trees.append(tree)
        else:
            print(f"Skipping invalid file: {path}")

    if not trees:
        print("No valid input files found.")
        return 1

    merged_tree = merge_trees(trees, args.strategy)
    merged_tree.write(args.output, encoding="utf-8", xml_declaration=True)
    print(f"Wrote merged file to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
