"""Simple ARXML merge utility with basic conflict resolution."""

import xml.etree.ElementTree as ET
import argparse
import json
import sys


def parse_arxml(path: str, encoding: str | None = None) -> ET.ElementTree | None:
    """Parse an ARXML file and return ElementTree or None on failure."""
    try:
        if encoding:
            with open(path, "r", encoding=encoding) as fh:
                tree = ET.parse(fh)
        else:
            tree = ET.parse(path)
    except (ET.ParseError, UnicodeDecodeError) as exc:
        print(f"Failed to parse {path}: {exc}", file=sys.stderr)
        return None

    root = tree.getroot()
    if _ns(root.tag) != "AUTOSAR":
        print(f"File {path} does not contain an AUTOSAR root element", file=sys.stderr)
        return None
    return tree


def _ns(tag: str) -> str:
    """Return a tag name with namespace stripped."""
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def parse_rules(path: str | None) -> dict:
    """Load rule definition JSON file if provided."""
    if not path:
        return {"replace_packages": []}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except OSError as exc:
        print(f"Failed to load rules file {path}: {exc}", file=sys.stderr)
        return {"replace_packages": []}
    if not isinstance(data, dict):
        print(f"Rules file {path} must contain a JSON object", file=sys.stderr)
        return {"replace_packages": []}
    rp = data.get("replace_packages")
    if not isinstance(rp, list):
        rp = []
    return {"replace_packages": [str(r) for r in rp]}


def merge_packages(
    base_pkg: ET.Element,
    new_pkg: ET.Element,
    strategy: str,
    ns: str,
    rules: dict | None = None,
) -> None:
    """Merge two AR-PACKAGES elements in-place recursively."""
    tag_pkg = f"{{{ns}}}AR-PACKAGE" if ns else "AR-PACKAGE"
    tag_pkgs = f"{{{ns}}}AR-PACKAGES" if ns else "AR-PACKAGES"
    tag_name = f"{{{ns}}}SHORT-NAME" if ns else "SHORT-NAME"

    base_map = {pkg.findtext(tag_name): pkg for pkg in base_pkg.findall(tag_pkg)}

    for pkg in new_pkg.findall(tag_pkg):
        name = pkg.findtext(tag_name)
        if name in base_map:
            if strategy == "interactive":
                choice = input(
                    f"Package '{name}' exists. Keep (o)ld, use (n)ew? [o/n]: "
                ).strip().lower()
                if choice.startswith("n"):
                    base_pkg.remove(base_map[name])
                    base_pkg.append(pkg)
                else:
                    base = base_map[name]
                    base_child = base.find(tag_pkgs)
                    new_child = pkg.find(tag_pkgs)
                    if base_child is not None and new_child is not None:
                        merge_packages(base_child, new_child, strategy, ns, rules)
                    elif base_child is None and new_child is not None:
                        base.append(new_child)
            elif strategy == "latest-wins":
                base_pkg.remove(base_map[name])
                base_pkg.append(pkg)
            elif strategy == "rule-based" and rules and name in rules.get("replace_packages", []):
                base_pkg.remove(base_map[name])
                base_pkg.append(pkg)
            else:  # conservative default
                base = base_map[name]
                base_child = base.find(tag_pkgs)
                new_child = pkg.find(tag_pkgs)
                if base_child is not None and new_child is not None:
                    merge_packages(base_child, new_child, strategy, ns, rules)
                elif base_child is None and new_child is not None:
                    base.append(new_child)
        else:
            base_pkg.append(pkg)


def merge_trees(
    trees: list[ET.ElementTree], strategy: str, rules: dict | None = None
) -> ET.ElementTree:
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
            merge_packages(base_pkgs, pkgs, strategy, ns, rules)

    return base_tree


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Merge multiple AUTOSAR ARXML files into a single output file.")
    parser.add_argument("output", help="Path to output ARXML file")
    parser.add_argument("inputs", nargs="+", help="Input ARXML files")
    parser.add_argument(
        "--encoding",
        help="Override input encoding (otherwise determined from XML header)",
    )
    parser.add_argument(
        "--strategy",
        choices=["conservative", "latest-wins", "interactive", "rule-based"],
        default="conservative",
        help="Conflict resolution strategy (default: conservative)",
    )
    parser.add_argument(
        "--rules",
        help="Path to JSON file defining rule-based merge behaviour",
    )
    args = parser.parse_args(argv)

    trees: list[ET.ElementTree] = []
    for path in args.inputs:
        tree = parse_arxml(path, args.encoding)
        if tree is not None:
            trees.append(tree)
        else:
            print(f"Skipping invalid file: {path}")

    if not trees:
        print("No valid input files found.")
        return 1

    rules = parse_rules(args.rules)
    merged_tree = merge_trees(trees, args.strategy, rules)
    merged_tree.write(args.output, encoding="utf-8", xml_declaration=True)
    print(f"Wrote merged file to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
