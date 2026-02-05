"""Command-line interface for census data extraction."""

import argparse
import sys
from pathlib import Path

from .extractor import (
    extract_census_data,
    list_columns,
    list_sheets,
    US_STATES,
)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="census-extract",
        description="Extract census data from Excel files for all 50 states + DC + national total"
    )
    parser.add_argument(
        "file",
        type=Path,
        help="Path to the Census Bureau Excel file"
    )
    parser.add_argument(
        "-v", "--variable",
        type=str,
        help="Variable name to search for and extract (searches column names)"
    )
    parser.add_argument(
        "-s", "--sheet",
        type=str,
        default="0",
        help="Sheet name or index (default: 0, first sheet)"
    )
    parser.add_argument(
        "-r", "--header-row",
        type=int,
        default=None,
        help="Row number to use as header (0-indexed). Auto-detect if not specified."
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Output file path (CSV). If not specified, prints to stdout."
    )
    parser.add_argument(
        "--list-columns",
        action="store_true",
        help="List all columns in the file and exit"
    )
    parser.add_argument(
        "--list-sheets",
        action="store_true",
        help="List all sheets in the file and exit"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )

    args = parser.parse_args()

    # Validate file exists
    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    # Parse sheet argument (could be name or index)
    try:
        sheet = int(args.sheet)
    except ValueError:
        sheet = args.sheet

    # Handle list options
    if args.list_sheets:
        sheets = list_sheets(args.file)
        print("Available sheets:")
        for i, name in enumerate(sheets):
            print(f"  [{i}] {name}")
        sys.exit(0)

    if args.list_columns:
        columns = list_columns(args.file, sheet)
        print("Available columns:")
        for col in columns:
            print(f"  - {col}")
        sys.exit(0)

    # Require variable for extraction
    if not args.variable:
        print("Error: --variable is required for extraction", file=sys.stderr)
        print("Use --list-columns to see available columns", file=sys.stderr)
        sys.exit(1)

    # Extract data
    try:
        result = extract_census_data(
            args.file,
            args.variable,
            sheet_name=sheet,
            header_row=args.header_row
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Report extraction results
    n_states = len(result[result["State"] != "United States"])
    has_national = "United States" in result["State"].values

    print(f"Extracted {n_states} states/territories" +
          (" + national total" if has_national else ""), file=sys.stderr)

    if n_states < 51:
        missing = set(US_STATES) - set(result["State"].values)
        if missing:
            print(f"Missing: {', '.join(sorted(missing))}", file=sys.stderr)

    # Output results
    if args.output:
        result.to_csv(args.output, index=False)
        print(f"Saved to: {args.output}", file=sys.stderr)
    else:
        print(result.to_csv(index=False))


if __name__ == "__main__":
    main()
