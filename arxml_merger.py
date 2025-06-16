import xml.etree.ElementTree as ET
import argparse
import sys


def parse_arxml(path: str) -> ET.ElementTree | None:
    """Parse an ARXML file and return ElementTree or None on failure."""
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        print(f"Failed to parse {path}: {exc}")
        return None
    return tree


def merge_trees(trees: list[ET.ElementTree]) -> ET.ElementTree:
    """Merge multiple AUTOSAR trees by appending root children."""
    base_tree = trees[0]
    base_root = base_tree.getroot()

    for t in trees[1:]:
        root = t.getroot()
        for child in root:
            base_root.append(child)
    return base_tree


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Merge multiple AUTOSAR ARXML files into a single output file.")
    parser.add_argument("output", help="Path to output ARXML file")
    parser.add_argument("inputs", nargs="+", help="Input ARXML files")
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

    merged_tree = merge_trees(trees)
    merged_tree.write(args.output, encoding="utf-8", xml_declaration=True)
    print(f"Wrote merged file to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
