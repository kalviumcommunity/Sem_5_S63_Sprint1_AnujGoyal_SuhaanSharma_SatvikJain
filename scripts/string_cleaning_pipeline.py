"""
String Cleaning Pipeline for Customer Database Integration.

Standardizes messy text from three data sources:
  - Product names with extra spaces / inconsistent casing
  - Customer segments with special characters and abbreviation variants
  - Locations with international/accented characters

Tasks covered
  1. Strip whitespace consistently
  2. Normalize casing to a consistent standard
  3. Remove special characters using regex
  4. Standardize categorical labels with a mapping dictionary
  5. Reusable clean_text_column function
"""

import re
import os
import pandas as pd
import numpy as np
from datetime import datetime

# ---------------------------------------------------------------------------
# Synthetic dataset
# ---------------------------------------------------------------------------

RAW_DATA = {
    "customer_id": [
        "C001", "C002", "C003", "C004", "C005", "C006",
        "C007", "C008", "C009", "C010", "C011", "C012",
        "C013", "C014", "C015",
    ],
    "product_name": [
        # 3 casing variants + whitespace variant to prove strip consolidation
        " Electronics ",        # leading+trailing space -> "Electronics"
        "Electronics",          # already clean  -> "Electronics" (same after strip)
        "electronics",
        "ELECTRONICS",
        " Home Appliances ",
        "Home Appliances",      # same as stripped variant above
        "home appliances",
        "HOME APPLIANCES",
        " Clothing ",
        "Clothing",             # same as stripped variant above
        "clothing",
        "CLOTHING",
        "Sports & Outdoor",
        "sports & outdoor",
        "SPORTS & OUTDOOR",
    ],
    "segment": [
        "B2B",
        " B2B ",               # whitespace variant -> consolidates with B2B after strip
        "b2b",
        "B 2 B",
        "b2 b",
        "business-to-business",
        "SME",
        " SME ",               # whitespace variant -> consolidates with SME after strip
        "sme",
        "small medium enterprise",
        "Enterprise",
        " Enterprise ",        # whitespace variant -> consolidates with Enterprise after strip
        "enterprise",
        "ENTERPRISE",
        "B2B",
    ],
    "location": [
        "Sao Paulo",            # no accent (clean reference)
        "São Paulo",  # Sao Paulo with tilde  -> accented
        "Montréal",        # Montreal with accent
        "Montreal",             # clean reference
        "New York",
        " New York ",           # whitespace duplicate
        "Bogotá",          # Bogota with accent
        "México City",     # Mexico with accent
        "München",         # Munich with umlaut
        "Munich",               # clean reference
        "Zürich",          # Zurich with umlaut
        "New Delhi",
        "Kraków",          # Krakow with accent
        "Montreal",             # duplicate
        "New York",             # duplicate
    ],
    "sales_rep": [
        "JOHN DOE",
        "john doe",
        "John Doe",
        "  Jane Smith  ",       # whitespace variant
        "Jane Smith",           # same after strip
        "JANE SMITH",
        "jane smith",
        "  Bob Johnson  ",      # whitespace variant
        "Bob Johnson",          # same after strip
        "BOB JOHNSON",
        "bob johnson",
        " Alice Brown ",
        "Alice Brown",          # same after strip
        "ALICE BROWN",
        "alice brown",
    ],
}


def create_sample_dataset() -> pd.DataFrame:
    return pd.DataFrame(RAW_DATA)


# ---------------------------------------------------------------------------
# Task 1 -- Strip whitespace consistently
# ---------------------------------------------------------------------------

def strip_all_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Strip leading/trailing whitespace from every string column."""
    string_cols = df.select_dtypes(include=["object", "str"]).columns

    print("\n" + "=" * 60)
    print("TASK 1: STRIP WHITESPACE")
    print("=" * 60)

    total_fixed = 0

    for col in string_cols:
        before_unique = df[col].nunique()
        before_counts = df[col].value_counts()

        df[col] = df[col].str.strip()

        after_unique = df[col].nunique()
        after_counts = df[col].value_counts()
        delta = before_unique - after_unique
        total_fixed += max(delta, 0)

        print(f"\nColumn: {col}")
        print(f"  Unique values before strip: {before_unique}")
        print(f"  Unique values after strip:  {after_unique}")
        print(f"  Values consolidated by stripping whitespace: {max(delta, 0)}")

        # Show the specific values that changed
        changed_values = []
        for val in before_counts.index:
            stripped = val.strip() if isinstance(val, str) else val
            if stripped != val:
                changed_values.append((repr(val), repr(stripped)))

        if changed_values:
            print(f"  Whitespace variants found (before -> after strip):")
            for raw, clean in changed_values:
                print(f"    {raw} -> {clean}")

    print(f"\nTotal whitespace issues fixed across all columns: {total_fixed}")

    # Before/after value_counts for key columns
    for col in ["product_name", "segment"]:
        print(f"\n  value_counts for [{col}] after strip:")
        print(df[col].value_counts().to_string())

    return df


# ---------------------------------------------------------------------------
# Task 2 -- Normalize casing to a consistent standard
# ---------------------------------------------------------------------------

LOWERCASE_COLUMNS = ["product_name", "segment", "sales_rep", "location"]


def normalize_casing(df: pd.DataFrame, columns_to_lower: list) -> pd.DataFrame:
    """
    Convert categorical text columns to lowercase.

    Business decision: lowercase chosen as the canonical standard because:
    - It is the default in SQL/analytics GROUP BY expressions
    - Prevents "JOHN", "john", "John" from creating three separate groups in groupby
    - Is the expected input format for the mapping dictionary in Task 4
    """
    print("\n" + "=" * 60)
    print("TASK 2: NORMALIZE CASING")
    print("=" * 60)
    print("Standard chosen: lowercase")
    print("Why: 'JOHN', 'john', 'John' all become 'john' -> one group in groupby\n")

    for col in columns_to_lower:
        if col not in df.columns:
            continue

        before_unique = df[col].nunique()
        sample_before = df[col].head(6).tolist()

        df[col] = df[col].str.lower()

        after_unique = df[col].nunique()
        sample_after = df[col].head(6).tolist()

        print(f"Column: {col}")
        print(f"  Unique values before: {before_unique}  ->  after: {after_unique}  (consolidated: {before_unique - after_unique})")
        print(f"  Before: {sample_before}")
        print(f"  After:  {sample_after}\n")

    print("Sample rows after casing normalization:")
    print(df[["product_name", "segment", "sales_rep"]].head(6).to_string())

    return df


# ---------------------------------------------------------------------------
# Task 3 -- Remove special characters using regex
# ---------------------------------------------------------------------------

SPECIAL_CHAR_PATTERN = r"[^a-zA-Z0-9 ]"

SPECIAL_CHAR_COLUMNS = ["location"]


def remove_special_characters(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """
    Remove non-alphanumeric characters (except spaces) from specified columns.

    Pattern [^a-zA-Z0-9 ] explanation:
      [^...]   negated character class -- matches anything NOT in the set
      a-zA-Z   keeps all English letters
      0-9      keeps digits
      (space)  keeps a single space
      Strips: accented letters (e ao u), &, _, -, etc.

    São Paulo -> Sao Paulo   (tilde removed from a)
    Montréal  -> Montreal    (acute removed from e)
    München   -> Munchen     (umlaut removed from u)
    """
    print("\n" + "=" * 60)
    print("TASK 3: REMOVE SPECIAL CHARACTERS")
    print("=" * 60)
    print(f"Regex pattern: '{SPECIAL_CHAR_PATTERN}'")
    print("Keeps: a-z A-Z 0-9 and space. Removes everything else (accents, symbols).\n")

    for col in columns:
        if col not in df.columns:
            continue

        before = df[col].copy()
        df[col] = df[col].str.replace(SPECIAL_CHAR_PATTERN, "", regex=True)

        changed_mask = before != df[col]
        print(f"Column: {col}")
        print(f"  Values with international/special characters cleaned: {changed_mask.sum()}")
        print(f"  Before -> After samples:")

        comparison = pd.DataFrame({"before": before[changed_mask], "after": df[col][changed_mask]})
        for _, row in comparison.iterrows():
            print(f"    {repr(row['before'])} -> {repr(row['after'])}")

        print(f"\n  Unique values after cleaning:")
        print(f"  {sorted(df[col].unique().tolist())}")

    return df


# ---------------------------------------------------------------------------
# Task 4 -- Standardize categorical labels using a mapping dictionary
# ---------------------------------------------------------------------------

# Business justifications:
#   B2B        - all-caps matches CRM system field standard; abbreviation preferred by sales team
#   SMB        - "Small-Medium Business" replaces legacy "SME" to align with new org taxonomy
#   Enterprise - Title-case used in contracts and financial reporting

SEGMENT_MAP = {
    "b2b": "B2B",
    "b 2 b": "B2B",
    "b2 b": "B2B",
    "business-to-business": "B2B",
    "sme": "SMB",
    "smb": "SMB",
    "small medium enterprise": "SMB",
    "enterprise": "Enterprise",
}

PRODUCT_MAP = {
    "electronics": "Electronics",
    "home appliances": "Home Appliances",
    "clothing": "Clothing",
    "sports  outdoor": "Sports & Outdoor",
    "sports outdoor": "Sports & Outdoor",
    "sports & outdoor": "Sports & Outdoor",
}


def standardize_categorical_labels(
    df: pd.DataFrame,
    column: str,
    mapping: dict,
    label: str = "",
) -> pd.DataFrame:
    """Apply mapping dictionary to consolidate label variants into canonical forms."""
    if column not in df.columns:
        return df

    before_counts = df[column].value_counts().sort_index()
    before_unique = df[column].nunique()

    df[column] = df[column].map(mapping).fillna(df[column])

    after_counts = df[column].value_counts().sort_index()
    after_unique = df[column].nunique()

    print(f"\nColumn: {column}  [{label}]")
    print(f"  Unique values: {before_unique} -> {after_unique}  (consolidated: {before_unique - after_unique})")
    print("  Value counts BEFORE mapping:")
    for k, v in before_counts.items():
        print(f"    {repr(k)}: {v}")
    print("  Value counts AFTER mapping:")
    for k, v in after_counts.items():
        print(f"    {repr(k)}: {v}")

    return df


def apply_all_mappings(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all categorical mapping dictionaries and print business justifications."""
    print("\n" + "=" * 60)
    print("TASK 4: STANDARDIZE CATEGORICAL LABELS")
    print("=" * 60)

    print("Segment mapping business decisions:")
    print("  b2b / b 2 b / b2 b / business-to-business -> 'B2B'")
    print("    Reason: CRM system stores B2B (all-caps); matches sales team reporting standard")
    print("  sme / small medium enterprise -> 'SMB'")
    print("    Reason: org restructuring renamed SME to SMB in Q3 reporting")
    print("  enterprise / ENTERPRISE -> 'Enterprise'")
    print("    Reason: title-case used in contracts and financial dashboards")

    print("\nProduct mapping business decisions:")
    print("  All case variants -> Title Case canonical form")
    print("    Reason: product catalog displays use Title Case for readability")

    df = standardize_categorical_labels(df, "segment", SEGMENT_MAP, "B2B/SMB/Enterprise variants")
    df = standardize_categorical_labels(df, "product_name", PRODUCT_MAP, "product name normalization")

    return df


# ---------------------------------------------------------------------------
# Task 5 -- Reusable clean_text_column function
# ---------------------------------------------------------------------------

def clean_text_column(
    series: pd.Series,
    lowercase: bool = True,
    strip: bool = True,
    remove_special: bool = False,
    mapping: dict = None,
) -> pd.Series:
    """
    Reusable text cleaning function applicable to any string column.

    Parameters
    ----------
    series         : Input pandas Series (string/object dtype)
    lowercase      : Convert to lowercase when True
    strip          : Strip leading/trailing whitespace when True
    remove_special : Remove non-alphanumeric characters via regex [^a-zA-Z0-9 ]
    mapping        : Optional dict mapping variant labels to canonical forms

    Returns
    -------
    Cleaned pandas Series. Null values (NaN/None) are preserved unchanged.
    """
    result = series.copy()

    null_count = result.isna().sum()
    if null_count > 0:
        print(f"  Warning: {null_count} null value(s) detected -- preserved as NaN")

    if strip:
        result = result.str.strip()

    if lowercase:
        result = result.str.lower()

    if remove_special:
        result = result.str.replace(SPECIAL_CHAR_PATTERN, "", regex=True)

    if mapping:
        result = result.map(mapping).fillna(result)

    return result


def demonstrate_reusable_function(df: pd.DataFrame) -> pd.DataFrame:
    """Show clean_text_column applied to multiple columns with different parameter combinations."""
    print("\n" + "=" * 60)
    print("TASK 5: REUSABLE clean_text_column FUNCTION")
    print("=" * 60)

    print("\n[sales_rep]  lowercase=True, strip=True, remove_special=False")
    print("  Why: names use only standard chars; we just need canonical casing")
    df["sales_rep"] = clean_text_column(
        df["sales_rep"], lowercase=True, strip=True, remove_special=False
    )
    print(df["sales_rep"].value_counts().to_string())

    print("\n[location]  lowercase=True, strip=True, remove_special=True")
    print("  Why: international cities have accented chars that break downstream ASCII systems")
    df["location"] = clean_text_column(
        df["location"], lowercase=True, strip=True, remove_special=True
    )
    print(df["location"].value_counts().to_string())

    print("\n[segment]  lowercase=True, strip=True, mapping=SEGMENT_MAP")
    print("  Why: need canonical B2B/SMB/Enterprise labels matching CRM; lowercase first so map keys match")
    df["segment"] = clean_text_column(
        df["segment"], lowercase=True, strip=True, remove_special=False, mapping=SEGMENT_MAP
    )
    print(df["segment"].value_counts().to_string())

    return df


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------

def run_edge_case_tests():
    """Verify clean_text_column handles boundary inputs correctly."""
    print("\n" + "=" * 60)
    print("EDGE CASE TESTING")
    print("=" * 60)

    test_cases = [
        "  Product A  ",   # leading/trailing spaces
        "PRODUCT B",       # all caps
        "Product_C",       # underscore (special char)
        None,              # null value
        "",                # empty string
    ]

    test_series = pd.Series(test_cases, dtype=object)

    print("Input values:")
    for i, v in enumerate(test_cases):
        print(f"  [{i}] {repr(v)}")

    result = clean_text_column(
        test_series,
        lowercase=True,
        strip=True,
        remove_special=True,
    )

    print("\nOutput after clean_text_column(lowercase=True, strip=True, remove_special=True):")
    for i, v in enumerate(result):
        print(f"  [{i}] {repr(v)}")

    assert result[0] == "product a",  f"strip test failed: {repr(result[0])}"
    assert result[1] == "product b",  f"lowercase test failed: {repr(result[1])}"
    assert result[2] == "productc",   f"special-char test failed: {repr(result[2])}"
    assert pd.isna(result[3]),        f"null preservation failed: {repr(result[3])}"
    assert result[4] == "",           f"empty string test failed: {repr(result[4])}"

    print("\nAll 5 edge-case assertions passed.")


# ---------------------------------------------------------------------------
# Final summary report
# ---------------------------------------------------------------------------

def print_final_summary(df_before: pd.DataFrame, df_after: pd.DataFrame):
    print("\n" + "=" * 60)
    print("FINAL PIPELINE SUMMARY")
    print("=" * 60)

    string_cols = df_before.select_dtypes(include=["object", "str"]).columns
    total_fixed = 0

    for col in string_cols:
        unique_before = df_before[col].nunique()
        unique_after = df_after[col].nunique()
        delta = max(unique_before - unique_after, 0)
        total_fixed += delta
        print(f"  {col:<20} {unique_before:>3} unique -> {unique_after:>3} unique  (consolidated {delta})")

    print(f"\n  Total variant entries consolidated: {total_fixed}")
    print(f"  Rows processed:  {len(df_after)}")
    print(f"  Columns cleaned: {len(string_cols)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("STRING CLEANING PIPELINE")
    print("Customer Database Integration")
    print("=" * 60)

    df_raw = create_sample_dataset()
    df = df_raw.copy()

    print(f"\nLoaded synthetic dataset: {len(df)} rows x {len(df.columns)} columns")
    print("Columns:", list(df.columns))
    print("\nRaw sample (first 6 rows):")
    print(df.head(6).to_string())

    # Task 1
    df = strip_all_strings(df)

    # Task 2
    df = normalize_casing(df, LOWERCASE_COLUMNS)

    # Task 3
    df = remove_special_characters(df, SPECIAL_CHAR_COLUMNS)

    # Task 4
    df = apply_all_mappings(df)

    # Task 5
    df = demonstrate_reusable_function(df)

    # Edge cases
    run_edge_case_tests()

    # Summary
    print_final_summary(df_raw, df)

    # Persist output
    os.makedirs("output", exist_ok=True)
    df.to_csv("output/cleaned_customer_data.csv", index=False)
    print("\nCleaned dataset saved to output/cleaned_customer_data.csv")
