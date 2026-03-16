from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

import pandas as pd


DEFAULT_INPUT_FILE = "processed/cancer_analytics.csv"

VALID_SEX_VALUES = {"Females", "Males", "Persons"}
VALID_STATES = {
    "NSW", "VIC", "QLD", "WA", "SA", "TAS", "ACT", "NT",
    "New South Wales", "Victoria", "Queensland", "Western Australia",
    "South Australia", "Tasmania", "Australian Capital Territory", "Northern Territory"
}


def clean_column_name(col: str) -> str:
    return " ".join(str(col).strip().split()).lower()


def find_column(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    normalized = {clean_column_name(col): col for col in df.columns}
    for candidate in candidates:
        key = clean_column_name(candidate)
        if key in normalized:
            return normalized[key]
    return None


def load_dataset(input_file: Path) -> pd.DataFrame:
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    if input_file.suffix.lower() == ".csv":
        df = pd.read_csv(input_file)
    elif input_file.suffix.lower() in {".xlsx", ".xls"}:
        df = pd.read_excel(input_file)
    else:
        raise ValueError("Unsupported input file type. Use CSV or Excel.")

    df.columns = [str(col).strip() for col in df.columns]
    return df


def validate_required_columns(df: pd.DataFrame) -> list[str]:
    issues: list[str] = []

    possible_cols = {
        "state": ["state", "state or territory"],
        "year": ["year"],
        "sex": ["sex", "gender"],
        "age_group": ["age_group", "age group", "age group (years)"],
        "cases": ["cases", "number", "count"],
        "incidence_rate": ["incidence_rate", "incidence rate", "rate", "age-standardised rate (per 100,000)"],
    }

    found = {}
    for logical_name, candidates in possible_cols.items():
        found[logical_name] = find_column(df, candidates)

    if found["state"] is None:
        issues.append("Missing state column.")
    if found["year"] is None:
        issues.append("Missing year column.")
    if found["cases"] is None and found["incidence_rate"] is None:
        issues.append("Missing both cases and incidence_rate columns.")

    return issues


def validate_years(df: pd.DataFrame, year_col: str) -> list[str]:
    issues: list[str] = []

    year_values = pd.to_numeric(df[year_col], errors="coerce")
    invalid_years = df[year_values.isna()][year_col].dropna().unique().tolist()
    if invalid_years:
        issues.append(f"Invalid year values found: {invalid_years[:10]}")

    valid_years = year_values.dropna()
    if not valid_years.empty:
        if (valid_years < 1900).any() or (valid_years > 2100).any():
            issues.append("Some year values are outside the expected range 1900-2100.")

    return issues


def validate_sex(df: pd.DataFrame, sex_col: str) -> list[str]:
    issues: list[str] = []

    unique_values = (
        df[sex_col]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    invalid = [value for value in unique_values if value not in VALID_SEX_VALUES]
    if invalid:
        issues.append(f"Unexpected sex values found: {invalid[:10]}")

    return issues


def validate_states(df: pd.DataFrame, state_col: str) -> list[str]:
    issues: list[str] = []

    empty_states = df[state_col].isna().sum()
    if empty_states > 0:
        issues.append(f"Found {empty_states} rows with missing state values.")

    unique_states = (
        df[state_col]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    invalid_states = [value for value in unique_states if value not in VALID_STATES]
    if invalid_states:
        issues.append(f"Unexpected state values found: {invalid_states[:10]}")

    return issues


def validate_numeric_column(df: pd.DataFrame, col_name: str) -> list[str]:
    issues: list[str] = []

    numeric_values = pd.to_numeric(df[col_name], errors="coerce")
    invalid_count = numeric_values.isna().sum() - df[col_name].isna().sum()
    if invalid_count > 0:
        issues.append(f"Column '{col_name}' contains {invalid_count} non-numeric values.")

    negative_count = (numeric_values.dropna() < 0).sum()
    if negative_count > 0:
        issues.append(f"Column '{col_name}' contains {negative_count} negative values.")

    return issues


def validate_missing_values(df: pd.DataFrame) -> list[str]:
    issues: list[str] = []

    missing_summary = df.isna().sum()
    missing_summary = missing_summary[missing_summary > 0]

    for col, count in missing_summary.items():
        issues.append(f"Column '{col}' has {count} missing values.")

    return issues


def validate_duplicates(df: pd.DataFrame) -> list[str]:
    issues: list[str] = []

    duplicate_count = df.duplicated().sum()
    if duplicate_count > 0:
        issues.append(f"Found {duplicate_count} duplicate rows.")

    return issues


def validate_age_group(df: pd.DataFrame, age_col: str) -> list[str]:
    issues: list[str] = []

    unique_ages = (
        df[age_col]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    if len(unique_ages) == 0:
        issues.append("Age group column exists but contains no usable values.")

    return issues


def run_validation(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    checks_passed: list[str] = []

    state_col = find_column(df, ["state", "state or territory"])
    year_col = find_column(df, ["year"])
    sex_col = find_column(df, ["sex", "gender"])
    age_col = find_column(df, ["age_group", "age group", "age group (years)"])
    cases_col = find_column(df, ["cases", "number", "count"])
    rate_col = find_column(df, ["incidence_rate", "incidence rate", "rate", "age-standardised rate (per 100,000)"])

    required_issues = validate_required_columns(df)
    if required_issues:
        issues.extend(required_issues)
    else:
        checks_passed.append("Required columns check passed.")

    if year_col:
        year_issues = validate_years(df, year_col)
        if year_issues:
            issues.extend(year_issues)
        else:
            checks_passed.append("Year validation passed.")

    if sex_col:
        sex_issues = validate_sex(df, sex_col)
        if sex_issues:
            issues.extend(sex_issues)
        else:
            checks_passed.append("Sex validation passed.")

    if state_col:
        state_issues = validate_states(df, state_col)
        if state_issues:
            issues.extend(state_issues)
        else:
            checks_passed.append("State validation passed.")

    if age_col:
        age_issues = validate_age_group(df, age_col)
        if age_issues:
            issues.extend(age_issues)
        else:
            checks_passed.append("Age group validation passed.")

    if cases_col:
        cases_issues = validate_numeric_column(df, cases_col)
        if cases_issues:
            issues.extend(cases_issues)
        else:
            checks_passed.append("Cases numeric validation passed.")

    if rate_col:
        rate_issues = validate_numeric_column(df, rate_col)
        if rate_issues:
            issues.extend(rate_issues)
        else:
            checks_passed.append("Incidence rate numeric validation passed.")

    duplicate_issues = validate_duplicates(df)
    if duplicate_issues:
        issues.extend(duplicate_issues)
    else:
        checks_passed.append("Duplicate row validation passed.")

    missing_issues = validate_missing_values(df)
    if missing_issues:
        issues.extend(missing_issues)
    else:
        checks_passed.append("Missing value validation passed.")

    return checks_passed, issues


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate processed cancer analytics dataset."
    )
    parser.add_argument(
        "--input-file",
        default=DEFAULT_INPUT_FILE,
        help=f"Path to the processed dataset. Default: {DEFAULT_INPUT_FILE}",
    )
    args = parser.parse_args()

    input_file = Path(args.input_file)
    df = load_dataset(input_file)

    print(f"\nLoaded dataset: {input_file}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}\n")

    checks_passed, issues = run_validation(df)

    print("Validation summary")
    print("-" * 60)

    if checks_passed:
        print("\nPassed checks:")
        for item in checks_passed:
            print(f"  - {item}")

    if issues:
        print("\nIssues found:")
        for item in issues:
            print(f"  - {item}")
    else:
        print("\nNo validation issues found. Dataset looks clean.")

    print("")


if __name__ == "__main__":
    main()