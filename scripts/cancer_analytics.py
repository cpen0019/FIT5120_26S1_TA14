from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd


INPUT_FILE = "filtered_datasets/aihw-can-122-CDiA-2023-Book-7-Cancer-incidence-by-state-and-territory__melanoma_of_the_skin.csv"
OUTPUT_FILE = "processed/cancer_analytics.csv"

INVALID_STATE_VALUES = {"Australia"}


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


def prepare_cancer_analytics() -> None:
    input_path = Path(INPUT_FILE)
    output_path = Path(OUTPUT_FILE)

    df = load_dataset(input_path)

    state_col = find_column(df, ["State", "State or Territory"])
    year_col = find_column(df, ["Year"])
    sex_col = find_column(df, ["Sex", "Gender"])
    age_col = find_column(df, ["Age group (years)", "Age group"])
    cases_col = find_column(df, ["Cases", "Number", "Count", "Number of cases"])
    rate_col = find_column(
        df,
        [
            "Age-standardised rate (per 100,000)",
            "Incidence rate",
            "Rate",
            "Age-standardised incidence rate (per 100,000)",
        ],
    )

    if state_col is None:
        raise ValueError("State column not found.")
    if year_col is None:
        raise ValueError("Year column not found.")
    if sex_col is None:
        raise ValueError("Sex column not found.")
    if cases_col is None:
        raise ValueError("Cases/Number/Count column not found.")

    analytics_df = pd.DataFrame()

    analytics_df["state"] = df[state_col].astype(str).str.strip()
    analytics_df["year"] = pd.to_numeric(df[year_col], errors="coerce")
    analytics_df["sex"] = df[sex_col].astype(str).str.strip()
    analytics_df["cases"] = pd.to_numeric(df[cases_col], errors="coerce")

    if age_col is not None:
        analytics_df["age_group"] = df[age_col].astype(str).str.strip()

    if rate_col is not None:
        analytics_df["incidence_rate"] = pd.to_numeric(df[rate_col], errors="coerce")

    analytics_df = analytics_df.dropna(how="all")

    # Remove national aggregate rows for state-level analytics
    analytics_df = analytics_df[~analytics_df["state"].isin(INVALID_STATE_VALUES)]

    # Remove rows with missing cases
    analytics_df = analytics_df.dropna(subset=["cases"])

    # Remove rows with missing essential fields
    analytics_df = analytics_df.dropna(subset=["state", "year", "sex"])

    # Convert year to integer-like nullable type
    analytics_df["year"] = analytics_df["year"].astype("Int64")

    # Remove duplicates
    analytics_df = analytics_df.drop_duplicates().reset_index(drop=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    analytics_df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print("Cancer analytics dataset created successfully.")
    print(f"Output file: {output_path}")
    print(f"Rows saved: {len(analytics_df)}")
    print("\nPreview:")
    print(analytics_df.head())


if __name__ == "__main__":
    prepare_cancer_analytics()