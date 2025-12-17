"""
PseudoBank - Pseudonymize Your Reports

This tool replaces sensitive values (like vendor names, program names) with
fake placeholder names (like Vendor_047, Program_012) so you can safely
share your data with AI tools.

Usage:
    python pseudonymize.py --input FILE    # Interactive mode (recommended!)
"""

import argparse
import random
import sys
from pathlib import Path

import pandas as pd

# Add the src folder to path so imports work
sys.path.insert(0, str(Path(__file__).parent))

from config import OUTPUT_FOLDER, INPUT_FOLDER


class SessionMapper:
    """
    Simple in-memory mapper for a single pseudonymization session.

    - Assigns RANDOM numbers (not sequential)
    - Consistent within the session (same value = same fake name)
    - No persistence - fresh mappings each time you run the tool
    """

    def __init__(self):
        # Structure: {prefix: {real_value: fake_value}}
        self._mappings = {}
        # Track used numbers per prefix to avoid duplicates
        self._used_numbers = {}

    def _get_random_number(self, prefix: str) -> int:
        """Get a random unused number for this prefix."""
        if prefix not in self._used_numbers:
            self._used_numbers[prefix] = set()

        used = self._used_numbers[prefix]

        # Pick from a range of 001-999
        available = [n for n in range(1, 1000) if n not in used]

        if not available:
            # Extremely unlikely, but fallback to sequential if we somehow use 999 values
            return len(used) + 1000

        chosen = random.choice(available)
        used.add(chosen)
        return chosen

    def get_fake_value(self, prefix: str, real_value: str) -> str:
        """
        Get the fake value for a real value.
        Creates a new random mapping if this value hasn't been seen.
        """
        if prefix not in self._mappings:
            self._mappings[prefix] = {}

        if real_value not in self._mappings[prefix]:
            # New value - assign a random number
            num = self._get_random_number(prefix)
            fake = f"{prefix}_{str(num).zfill(3)}"
            self._mappings[prefix][real_value] = fake

        return self._mappings[prefix][real_value]

    def get_summary(self) -> dict:
        """Get a summary of mappings created this session."""
        return {prefix: len(mappings) for prefix, mappings in self._mappings.items()}


def load_file(file_path: Path) -> pd.DataFrame:
    """Load a report file (Excel or CSV)."""
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = file_path.suffix.lower()

    if suffix == '.csv':
        return pd.read_csv(file_path)
    elif suffix in ['.xlsx', '.xls']:
        return pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}. Use .csv, .xlsx, or .xls")


def save_file(df: pd.DataFrame, output_path: Path):
    """Save a DataFrame to file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    suffix = output_path.suffix.lower()

    if suffix == '.csv':
        df.to_csv(output_path, index=False)
    else:
        df.to_excel(output_path, index=False)


def print_header(text: str):
    """Print a nice header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_step(step_num: int, text: str):
    """Print a step indicator."""
    print(f"\n--- Step {step_num}: {text} ---\n")


def get_yes_no(prompt: str) -> bool:
    """Ask a yes/no question."""
    while True:
        response = input(f"{prompt} (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        print("Please enter 'y' for yes or 'n' for no.")


def interactive_pseudonymize(input_file: Path):
    """
    Interactive mode - walks you through pseudonymizing a file step by step.
    """
    print_header("PSEUDOBANK - Interactive Mode")

    print("""
WHAT THIS DOES:
    This tool helps you replace sensitive information in your report
    (like vendor names, program names) with fake placeholder names
    (like Vendor_047, Program_012).

    After this, you can safely share your data with AI tools.
    The numbers and dates stay the same - only the names change.

    NOTE: Each time you run this tool, you get FRESH random assignments.
    This makes it harder for anyone to reverse-engineer patterns.
    """)

    # -------------------------------------------------------------------------
    # STEP 1: Load the file
    # -------------------------------------------------------------------------
    print_step(1, "Loading your file")

    try:
        df = load_file(input_file)
        print(f"Loaded: {input_file.name}")
        print(f"Found {len(df)} rows of data")
    except Exception as e:
        print(f"ERROR: Could not load file. {e}")
        return

    # -------------------------------------------------------------------------
    # STEP 2: Show columns and explain
    # -------------------------------------------------------------------------
    print_step(2, "Looking at your columns")

    print("Your file has these columns:\n")
    for i, col in enumerate(df.columns, 1):
        # Show a sample value from each column
        sample = df[col].dropna().iloc[0] if len(df[col].dropna()) > 0 else "(empty)"
        # Truncate long samples
        sample_str = str(sample)
        if len(sample_str) > 30:
            sample_str = sample_str[:27] + "..."
        print(f"  {i}. {col}")
        print(f"      Example value: {sample_str}")
        print()

    # -------------------------------------------------------------------------
    # STEP 3: Select columns to pseudonymize
    # -------------------------------------------------------------------------
    print_step(3, "Select columns to hide")

    print("""
WHICH COLUMNS CONTAIN SENSITIVE INFORMATION?

Think about columns that have:
  - Company names (vendors, contractors, suppliers)
  - Program or project names
  - Organization names
  - Any other names you don't want to share

Columns you should usually KEEP as-is (don't select these):
  - Dollar amounts (these are usually fine)
  - Dates
  - Document numbers
  - Generic codes
    """)

    print("Enter the NUMBERS of the columns you want to hide.")
    print("Separate multiple numbers with commas.")
    print("Example: 1, 3, 5")
    print()

    columns_list = list(df.columns)
    selected_columns = []

    while True:
        response = input("Column numbers to hide (or 'none' to skip): ").strip()

        if response.lower() == 'none':
            break

        try:
            numbers = [int(x.strip()) for x in response.split(',')]
            selected_columns = []
            valid = True

            for num in numbers:
                if 1 <= num <= len(columns_list):
                    selected_columns.append(columns_list[num - 1])
                else:
                    print(f"  '{num}' is not a valid column number. Please try again.")
                    valid = False
                    break

            if valid:
                break

        except ValueError:
            print("  Please enter numbers separated by commas (e.g., 1, 3, 5)")

    if not selected_columns:
        print("\nNo columns selected. Your file will not be changed.")
        return

    print("\nYou selected these columns to hide:")
    for col in selected_columns:
        print(f"  - {col}")

    # -------------------------------------------------------------------------
    # STEP 4: Assign prefixes with VERY plain explanation
    # -------------------------------------------------------------------------
    print_step(4, "Choose replacement names")

    print("""
WHAT ARE PREFIXES?

When we hide a value like "Acme Corporation", we replace it with a
fake name like "Vendor_047".

The PREFIX is the word that comes before the number.

  Example:
    "Acme Corporation" becomes "Vendor_047"
    "Boeing Defense"   becomes "Vendor_128"
                                ^^^^^^
                                This is the PREFIX

The NUMBER is randomly assigned (not sequential like 001, 002, 003).
This makes patterns harder to guess.

COMMON PREFIXES TO USE:

  For company/vendor columns:     Vendor
  For program/project columns:    Program
  For contractor columns:         Contractor
  For organization columns:       Org

You can use any word you want! The prefix just helps you remember
what type of data it was.
    """)

    column_prefixes = {}

    for col in selected_columns:
        # Show some sample values from this column
        samples = df[col].dropna().unique()[:3]
        samples_str = ", ".join([str(s)[:20] for s in samples])

        print(f"\nColumn: '{col}'")
        print(f"Sample values: {samples_str}")
        print()

        while True:
            prefix = input(f"What prefix should I use for '{col}'? (e.g., Vendor, Program): ").strip()

            if prefix:
                # Clean up the prefix - capitalize first letter, remove spaces
                prefix = prefix.replace(" ", "_").title()
                column_prefixes[col] = prefix
                print(f"  Got it! Values in '{col}' will become {prefix}_XXX (random numbers)")
                break
            else:
                print("  Please enter a prefix (like 'Vendor' or 'Program')")

    # -------------------------------------------------------------------------
    # STEP 5: Confirm before proceeding
    # -------------------------------------------------------------------------
    print_step(5, "Confirm your choices")

    print("Here's what I'm about to do:\n")
    print(f"  File: {input_file.name}")
    print(f"  Rows: {len(df)}")
    print()
    print("  Columns to hide:")
    for col, prefix in column_prefixes.items():
        unique_count = df[col].nunique()
        print(f"    '{col}' -> {prefix}_XXX (random numbers, {unique_count} unique values)")
    print()
    print("  Columns that will stay the same:")
    unchanged = [c for c in df.columns if c not in selected_columns]
    for col in unchanged:
        print(f"    '{col}'")
    print()

    if not get_yes_no("Does this look right?"):
        print("\nCancelled. No changes made.")
        return

    # -------------------------------------------------------------------------
    # STEP 6: Do the pseudonymization
    # -------------------------------------------------------------------------
    print_step(6, "Replacing values")

    # Create a fresh mapper for this session
    mapper = SessionMapper()

    for col, prefix in column_prefixes.items():
        unique_before = df[col].nunique()

        def replace_value(value):
            if pd.isna(value):
                return value
            return mapper.get_fake_value(prefix, str(value))

        df[col] = df[col].apply(replace_value)

        print(f"  Replaced {unique_before} unique values in '{col}' with random {prefix}_XXX")

    # -------------------------------------------------------------------------
    # STEP 7: Save the output
    # -------------------------------------------------------------------------
    print_step(7, "Saving your clean file")

    output_path = OUTPUT_FOLDER / f"CLEAN_{input_file.name}"
    save_file(df, output_path)

    # -------------------------------------------------------------------------
    # DONE!
    # -------------------------------------------------------------------------
    print_header("DONE!")

    print(f"""
YOUR CLEAN FILE IS READY:

  {output_path}

WHAT TO DO NEXT:

  1. Open the clean file and verify it looks right
  2. Share the clean file with Claude or other AI tools
  3. When you get code back, run it on your ORIGINAL file
     (the code uses column names, not the fake values)

SECURITY NOTE:

  Each time you run this tool, values get NEW random numbers.
  "Acme Corp" might be Vendor_047 this time and Vendor_283 next time.
  This makes patterns harder to reverse-engineer.
    """)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="PseudoBank - Pseudonymize sensitive data in reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:

  Pseudonymize a report (interactive):
    python pseudonymize.py --input report.xlsx
    python pseudonymize.py --input "C:\\path\\to\\report.csv"

That's it! No setup required. Just point it at a file and go.
        """
    )

    parser.add_argument(
        '--input',
        type=str,
        help='Path to the file you want to pseudonymize'
    )

    args = parser.parse_args()

    # Handle --input (interactive pseudonymization)
    if args.input:
        # Resolve input path
        input_path = Path(args.input)

        # If not an absolute path and doesn't exist, check sample_data folder
        if not input_path.is_absolute() and not input_path.exists():
            input_path = INPUT_FOLDER / args.input

        if not input_path.exists():
            print(f"ERROR: File not found: {args.input}")
            print(f"  Tried: {Path(args.input).absolute()}")
            print(f"  Tried: {input_path}")
            sys.exit(1)

        interactive_pseudonymize(input_path)
        return

    # If no valid arguments, show help
    parser.print_help()


if __name__ == "__main__":
    main()
