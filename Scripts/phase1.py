#!/usr/bin/env python3

"""
Read a Wordly Wise–style JSON structure from STDIN and write a modified version
to STDOUT, with the following changes:

1. Add a root-level "seed" key whose value comes from the command-line argument
   --seed (also accepts ---seed for convenience).

2. Add a root-level "theme" key whose value is the full text contents of the
   file specified by --theme.

3. Optionally filter the "sections" array using --section. The --section
   argument may be:
   - A single integer: "3"
   - A comma-separated list: "1,3,5"
   - Ranges with dashes: "2-4"
   - Any combination: "1,3-5,7"

   If --section is omitted, all sections from the input are included unchanged.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Set, Optional


def parse_section_spec(spec: str) -> Set[int]:
    """
    Parse a section spec string like:
        "3"
        "1,3,5"
        "2-4"
        "1,3-5,7"
    into a set of integers { ... }.

    If any part cannot be parsed as an integer (or range of ints),
    a ValueError is raised.
    """
    sections: Set[int] = set()

    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue

        if "-" in chunk:
            # Range: e.g. "3-7"
            start_str, end_str = chunk.split("-", 1)
            try:
                start = int(start_str)
                end = int(end_str)
            except ValueError as exc:
                raise ValueError(f"Invalid section range: {chunk!r}") from exc

            # Allow reversed ranges like "7-3"
            if start > end:
                start, end = end, start

            for s in range(start, end + 1):
                sections.add(s)
        else:
            # Single integer
            try:
                sections.add(int(chunk))
            except ValueError as exc:
                raise ValueError(f"Invalid section value: {chunk!r}") from exc

    return sections


def build_output_structure(
    data: Dict[str, Any],
    seed: int,
    theme_text: str,
    section_filter: Optional[Set[int]],
) -> Dict[str, Any]:
    """
    Build the output JSON structure.

    - Preserves input_title (if present).
    - Adds root-level "seed" and "theme" keys.
    - Optionally filters "sections" based on section_filter.
    """
    # Start with seed and theme first, so "seed" is at the top of the output.
    output: Dict[str, Any] = {
        "seed": seed,
        "theme": theme_text,
    }

    # Keep existing top-level fields (except sections; we handle that separately).
    for key, value in data.items():
        if key == "sections":
            continue
        output[key] = value

    # Filter sections if needed
    all_sections: List[Dict[str, Any]] = data.get("sections", [])
    if not isinstance(all_sections, list):
        raise TypeError("Input JSON 'sections' field must be a list.")

    if section_filter is None:
        filtered_sections = all_sections
    else:
        filtered_sections = [
            s
            for s in all_sections
            if isinstance(s, dict) and s.get("section") in section_filter
        ]

    output["sections"] = filtered_sections
    return output


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        description="Augment and optionally filter a Wordly Wise–style JSON structure."
    )

    # Support both --seed and ---seed (user mentioned ---seed in the spec).
    parser.add_argument(
        "--seed",
        type=int,
        required=True,
        help="Integer seed value to include as the root-level 'seed' key.",
    )

    parser.add_argument(
        "--themepath",
        type=str,
        required=True,
        help="Path to a text file whose contents will be stored under the root-level 'themepath' key.",
    )

    parser.add_argument(
        "--section",
        type=str,
        default=None,
        help=(
            "Optional section filter. Examples: '3', '1,3,5', '2-4', or '1,3-5,7'. "
            "If omitted, all sections from the input are included."
        ),
    )

    args = parser.parse_args(argv)

    # Read and parse input JSON from stdin
    try:
        raw_input = sys.stdin.read()
        data = json.loads(raw_input)
    except json.JSONDecodeError as exc:
        print(f"Error: failed to parse JSON from STDIN: {exc}", file=sys.stderr)
        sys.exit(1)

    # Read theme file contents
    theme_path = Path(args.themepath)
    try:
        theme_text = theme_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Error: could not read theme file {theme_path!r}: {exc}", file=sys.stderr)
        sys.exit(1)

    # Parse section filter if provided
    section_filter: Set[int] | None = None
    if args.section is not None:
        try:
            section_filter = parse_section_spec(args.section)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    # Build the output structure
    try:
        output = build_output_structure(
            data=data,
            seed=args.seed,
            theme_text=theme_text,
            section_filter=section_filter,
        )
    except Exception as exc:  # broad catch to give a clear message on failure
        print(f"Error while building output structure: {exc}", file=sys.stderr)
        sys.exit(1)

    # Write pretty-printed JSON to stdout
    json.dump(output, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()

