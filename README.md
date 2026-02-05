# Census Extract

Extract data from Census Bureau Excel files for all 50 states + DC + national total.

## Installation

### Option 1: Install as Python package (recommended)

```bash
pip install .
```

After installation, use the `census-extract` command directly:

```bash
census-extract data.xlsx -v "Population"
```

### Option 2: Standalone executable

Build a standalone executable that works without Python installed:

```bash
# Install build dependencies
pip install ".[dev]"

# Build executable
python build.py

# Find executable in dist/
./dist/census-extract data.xlsx -v "Population"
```

## Usage

```bash
# List available sheets in a file
census-extract data.xlsx --list-sheets

# List available columns (to find your variable)
census-extract data.xlsx --list-columns

# Extract data for a specific variable (searches column names)
census-extract data.xlsx -v "Population"

# Save output to CSV
census-extract data.xlsx -v "Population" -o output.csv

# Specify a sheet by name or index
census-extract data.xlsx -v "Income" -s "Data"

# Specify header row if auto-detection fails (0-indexed)
census-extract data.xlsx -v "Median Income" -r 3
```

## Features

- **Variable search**: Use `-v` to search column names (case-insensitive partial match)
- **Auto-detection**: Automatically finds the state column and header row
- **Complete coverage**: Extracts all 50 states + DC + national total
- **Validation**: Reports any missing states

## Output

By default, outputs CSV to stdout. Use `-o` to save to a file.

```csv
State,Population
Alabama,5024279
Alaska,733391
...
```
