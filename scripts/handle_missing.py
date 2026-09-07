import sys
import pandas as pd
import numpy as np
import json
import os

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


# ─────────────────────────────────────────────
# Task 1 – Analyze Missing Values Before Treatment
# ─────────────────────────────────────────────

def analyze_missing_values(df):
    """
    Compute null counts and percentages before treatment.

    Returns: DataFrame with analysis of missing data by column
    """
    missing_analysis = pd.DataFrame({
        'column': df.columns,
        'null_count': df.isnull().sum().values,
        'null_percentage': (df.isnull().sum() / len(df) * 100).round(2).values,
        'data_type': df.dtypes.values,
        'null_meaning': ''  # To be filled based on column context
    })

    print("=" * 70)
    print("BEFORE IMPUTATION - Missing Value Analysis")
    print("=" * 70)
    print(missing_analysis.to_string(index=False))
    print(f"\nTotal rows: {len(df)}")
    print(f"Total cells: {len(df) * len(df.columns)}")
    print(f"Missing cells: {df.isnull().sum().sum()}")
    print("=" * 70)

    return missing_analysis


# ─────────────────────────────────────────────
# Task 2 – Imputation Strategy Functions
# ─────────────────────────────────────────────

def impute_mean_median(df, numerical_cols, strategy='median'):
    """Fill numerical nulls with mean or median."""
    df_imputed = df.copy()
    for col in numerical_cols:
        if col not in df_imputed.columns:
            continue
        null_count = df_imputed[col].isnull().sum()
        if null_count > 0:
            fill_value = (
                df_imputed[col].median()
                if strategy == 'median'
                else df_imputed[col].mean()
            )
            df_imputed[col] = df_imputed[col].fillna(fill_value)
            print(f"  ✓ {col}: filled {null_count} nulls with {strategy} ({fill_value:.2f})")
    return df_imputed


def impute_mode(df, categorical_cols):
    """Fill categorical nulls with mode (most common value)."""
    df_imputed = df.copy()
    for col in categorical_cols:
        if col not in df_imputed.columns:
            continue
        null_count = df_imputed[col].isnull().sum()
        if null_count > 0:
            mode_val = df_imputed[col].mode()[0]
            df_imputed[col] = df_imputed[col].fillna(mode_val)
            print(f"  ✓ {col}: filled {null_count} nulls with mode '{mode_val}'")
    return df_imputed


def impute_forward_fill(df, time_series_cols):
    """Fill with previous value (for time-series data)."""
    df_imputed = df.copy()
    for col in time_series_cols:
        if col not in df_imputed.columns:
            continue
        null_count = df_imputed[col].isnull().sum()
        if null_count > 0:
            df_imputed[col] = df_imputed[col].ffill()
            print(f"  ✓ {col}: forward-filled {null_count} nulls")
    return df_imputed


def drop_rows_with_nulls(df, critical_cols):
    """Drop rows where critical columns are null."""
    rows_before = len(df)
    existing_critical = [c for c in critical_cols if c in df.columns]
    df_imputed = df.dropna(subset=existing_critical)
    rows_dropped = rows_before - len(df_imputed)
    print(f"  ✓ Dropped {rows_dropped} rows with null in: {existing_critical}")
    return df_imputed


# ─────────────────────────────────────────────
# Task 3 – Document Imputation Decisions
# ─────────────────────────────────────────────

def document_imputation_decisions(df_original, df_imputed):
    """Document all imputation decisions with business justification."""

    decisions = {
        'amount': {
            'column_type': 'numerical',
            'null_count_before': int(df_original['amount'].isnull().sum()) if 'amount' in df_original else 0,
            'strategy': 'median_imputation',
            'value_used': float(round(df_original['amount'].median(), 2)) if 'amount' in df_original else None,
            'business_reasoning': (
                'Median purchase amount is representative of typical transaction. '
                'Mean would be skewed by high-value outliers. '
                'Maintains distribution integrity.'
            ),
            'risk_assessment': 'Low - median is stable metric resistant to outliers'
        },
        'email': {
            'column_type': 'categorical_identifier',
            'null_count_before': int(df_original['email'].isnull().sum()) if 'email' in df_original else 0,
            'strategy': 'drop_rows',
            'rows_affected': int(df_original['email'].isnull().sum()) if 'email' in df_original else 0,
            'business_reasoning': (
                'Email is critical for customer contact and marketing campaigns. '
                'Rows without email cannot be used for outreach. Data is incomplete.'
            ),
            'risk_assessment': 'Low - only affects small percentage of data'
        },
        'status_date': {
            'column_type': 'datetime_series',
            'null_count_before': int(df_original['status_date'].isnull().sum()) if 'status_date' in df_original else 0,
            'strategy': 'forward_fill',
            'interpretation': 'Assumes last known status date is still valid until changed',
            'business_reasoning': (
                'For time-series analysis, forward fill preserves temporal continuity. '
                'Status typically does not change frequently.'
            ),
            'risk_assessment': 'Medium - assumes no change between observations'
        },
        'name': {
            'column_type': 'categorical',
            'null_count_before': int(df_original['name'].isnull().sum()) if 'name' in df_original else 0,
            'strategy': 'mode_imputation',
            'value_used': str(df_original['name'].mode()[0]) if 'name' in df_original and not df_original['name'].mode().empty else None,
            'business_reasoning': (
                'Customer name is non-critical for aggregation but needed for display. '
                'Mode fill (most frequent name) avoids blank records in reports.'
            ),
            'risk_assessment': 'Low - name is not used in numerical computations'
        },
        'category': {
            'column_type': 'categorical',
            'null_count_before': int(df_original['category'].isnull().sum()) if 'category' in df_original else 0,
            'strategy': 'mode_imputation',
            'value_used': str(df_original['category'].mode()[0]) if 'category' in df_original and not df_original['category'].mode().empty else None,
            'business_reasoning': (
                'Product category drives segmentation and reporting. '
                'Mode fill assigns the most common category, preserving distribution shape.'
            ),
            'risk_assessment': 'Low - only a small fraction of records affected'
        },
        'customer_id': {
            'column_type': 'primary_key_identifier',
            'null_count_before': int(df_original['customer_id'].isnull().sum()) if 'customer_id' in df_original else 0,
            'strategy': 'drop_rows',
            'rows_affected': int(df_original['customer_id'].isnull().sum()) if 'customer_id' in df_original else 0,
            'business_reasoning': (
                'customer_id is the primary key. Records without it are unidentifiable '
                'and cannot be linked to any entity in the data model. '
                'They must be dropped — never imputed with a placeholder.'
            ),
            'risk_assessment': 'Low - primary key nulls are structurally invalid records'
        }
    }

    os.makedirs('output', exist_ok=True)
    with open('output/imputation_decisions.json', 'w') as f:
        json.dump(decisions, f, indent=2, default=str)

    print("  ✓ Decisions saved to output/imputation_decisions.json")
    return decisions


# ─────────────────────────────────────────────
# Task 4 – Compare Before and After Metrics
# ─────────────────────────────────────────────

def validate_imputation(df_original, df_imputed):
    """Compare metrics before and after imputation."""

    print("\n" + "=" * 70)
    print("AFTER IMPUTATION - Validation Report")
    print("=" * 70)
    print(f"Total rows before: {len(df_original)}")
    print(f"Total rows after:  {len(df_imputed)}")
    print(f"Rows removed: {len(df_original) - len(df_imputed)}")
    print(f"\nTotal nulls before: {df_original.isnull().sum().sum()}")
    print(f"Total nulls after:  {df_imputed.isnull().sum().sum()}")

    missing_after = pd.DataFrame({
        'column': df_imputed.columns,
        'null_count_after': df_imputed.isnull().sum().values,
        'null_percentage_after': (
            df_imputed.isnull().sum() / len(df_imputed) * 100
        ).round(2).values
    })

    print("\nNull values by column after imputation:")
    print(missing_after.to_string(index=False))
    print("=" * 70)

    return missing_after


# ─────────────────────────────────────────────
# Task 5 – Main Imputation Workflow
# ─────────────────────────────────────────────

if __name__ == "__main__":
    # Load data
    df_raw = pd.read_csv('data/raw/missing_data.csv')
    df_original = df_raw.copy()

    # Step 1: Analyze missing before treatment
    print("Step 1: Analyzing missing values...")
    analyze_missing_values(df_raw)

    # Step 2: Apply strategy-specific imputation
    print("\nStep 2: Applying imputation strategies...")

    # Drop rows with nulls in critical identifier columns
    df_clean = drop_rows_with_nulls(df_raw, ['customer_id', 'email'])

    # Impute numerical columns with median
    df_clean = impute_mean_median(df_clean, ['amount', 'quantity'], strategy='median')

    # Impute categorical columns with mode
    df_clean = impute_mode(df_clean, ['name', 'category', 'region'])

    # Impute time-series columns with forward fill
    df_clean = impute_forward_fill(df_clean, ['last_updated', 'status_date'])

    # Step 3: Document decisions
    print("\nStep 3: Documenting imputation decisions...")
    document_imputation_decisions(df_original, df_clean)

    # Step 4: Validate results
    print("\nStep 4: Validating imputation...")
    validate_imputation(df_original, df_clean)

    # Save cleaned data
    os.makedirs('data/processed', exist_ok=True)
    df_clean.to_csv('data/processed/cleaned_data.csv', index=False)
    print("\n✓ Cleaned data saved to data/processed/cleaned_data.csv")
