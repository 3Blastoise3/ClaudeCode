#!/usr/bin/env python3
"""
Census Bureau Excel Data Extractor

Reads Census Bureau Excel files and extracts data for all 50 states + DC + national total
for a specified variable (column).
"""

import argparse
import sys
from pathlib import Path

import pandas as pd


# Standard list of US states + DC for validation/filtering
US_STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
    "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
    "New Hampshire", "New Jersey", "New Mexico", "New York",
    "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
    "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
    "West Virginia", "Wisconsin", "Wyoming", "District of Columbia"
]

# Common variations for national total row
NATIONAL_LABELS = ["United States", "US", "USA", "National", "Total", "US Total"]


def find_variable_column(df: pd.DataFrame, search_term: str) -> str | None:
    """
    Search for a column containing the search term (case-insensitive).

    Args:
        df: DataFrame to search
        search_term: Term to search for in column names

    Returns:
        Matching column name or None if not found
    """
    search_lower = search_term.lower()
    matches = [col for col in df.columns if search_lower in str(col).lower()]

    if not matches:
        return None
    elif len(matches) == 1:
        return matches[0]
    else:
        # Return exact match if available, otherwise first match
        for col in matches:
            if str(col).lower() == search_lower:
                return col
        return matches[0]


def find_state_column(df: pd.DataFrame) -> str | None:
    """
    Attempt to find the column containing state names.

    Args:
        df: DataFrame to search

    Returns:
        Column name containing state data or None
    """
    # Common column names for state data
    state_col_names = ["state", "geography", "geo", "name", "area", "location"]

    # First, check column names
    for col in df.columns:
        col_lower = str(col).lower()
        if any(name in col_lower for name in state_col_names):
            return col

    # If not found by name, check content for state names
    for col in df.columns:
        try:
            col_values = df[col].astype(str).str.strip()
            state_matches = sum(1 for val in col_values if val in US_STATES)
            if state_matches >= 10:  # At least 10 states found
                return col
        except Exception:
            continue

    return None


def normalize_state_name(name: str) -> str | None:
    """
    Normalize a state name to standard format.

    Args:
        name: Input state name (possibly with extra whitespace or formatting)

    Returns:
        Normalized state name or None if not a valid state
    """
    if pd.isna(name):
        return None

    cleaned = str(name).strip()

    # Check for national total
    if any(label.lower() in cleaned.lower() for label in NATIONAL_LABELS):
        return "United States"

    # Check against known states
    for state in US_STATES:
        if state.lower() == cleaned.lower():
            return state

    return None


def extract_census_data(
    file_path: Path,
    variable: str,
    sheet_name: str | int = 0,
    header_row: int | None = None
) -> pd.DataFrame:
    """
    Extract census data for a specific variable from an Excel file.

    Args:
        file_path: Path to the Excel file
        variable: Variable/column name to search for and extract
        sheet_name: Sheet name or index to read
        header_row: Row number to use as header (0-indexed), auto-detect if None

    Returns:
        DataFrame with State and extracted variable columns
    """
    # Read the Excel file
    if header_row is not None:
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
    else:
        # Try to auto-detect header row by reading first few rows
        df_preview = pd.read_excel(file_path, sheet_name=sheet_name, header=None, nrows=20)

        # Look for row that contains state names or common headers
        header_row = 0
        for idx, row in df_preview.iterrows():
            row_str = ' '.join(str(v).lower() for v in row.values if pd.notna(v))
            if 'state' in row_str or 'geography' in row_str or any(s.lower() in row_str for s in US_STATES[:5]):
                header_row = idx
                break

        df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)

    # Find the state column
    state_col = find_state_column(df)
    if state_col is None:
        raise ValueError("Could not identify a column containing state names")

    # Find the variable column
    var_col = find_variable_column(df, variable)
    if var_col is None:
        available_cols = [str(c) for c in df.columns[:20]]
        raise ValueError(
            f"Could not find variable '{variable}' in columns. "
            f"Available columns (first 20): {available_cols}"
        )

    # Extract relevant columns
    result_df = df[[state_col, var_col]].copy()
    result_df.columns = ["State", variable]

    # Normalize state names and filter to valid states + national
    result_df["State_Normalized"] = result_df["State"].apply(normalize_state_name)
    result_df = result_df[result_df["State_Normalized"].notna()]
    result_df["State"] = result_df["State_Normalized"]
    result_df = result_df.drop(columns=["State_Normalized"])

    # Remove duplicates, keeping first occurrence
    result_df = result_df.drop_duplicates(subset=["State"], keep="first")

    return result_df


def list_columns(file_path: Path, sheet_name: str | int = 0) -> list[str]:
    """
    List all columns in the Excel file.

    Args:
        file_path: Path to the Excel file
        sheet_name: Sheet name or index

    Returns:
        List of column names
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=0)
    return list(df.columns)


def list_sheets(file_path: Path) -> list[str]:
    """
    List all sheet names in the Excel file.

    Args:
        file_path: Path to the Excel file

    Returns:
        List of sheet names
    """
    xl = pd.ExcelFile(file_path)
    return xl.sheet_names


def main():
    parser = argparse.ArgumentParser(
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
