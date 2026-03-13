from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

import pandas as pd


DEFAULT_INPUT_FILE = "filtered_datasets/aihw-can-122-CDiA-2023-Book-7-Cancer-incidence-by-state-and-territory__melanoma_of_the_skin.csv"
DEFAULT_OUTPUT_DIR = "processed"


def clean_column_name(col: str) -> str:
    return " ".join(str(col).strip().split()).lower()


def find_column(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    normalized = {clean_column_name(col): col for col in df.columns}
    for candidate in candidates:
        key = clean_column_name(candidate)
        if key in normalized:
            return normalized[key]
    return None


def ensure_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)


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


def prepare_base_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    state_col = find_column(df, ["State or Territory", "State", "Jurisdiction", "Region"])
    year_col = find_column(df, ["Year"])
    sex_col = find_column(df, ["Sex", "Gender"])
    age_col = find_column(df, ["Age group (years)", "Age group", "Age"])
    cancer_col = find_column(df, ["Cancer group/site", "Cancer site", "Cancer group"])
    rate_col = find_column(
        df,
        [
            "Age-standardised rate (per 100,000)",
            "ASR (per 100,000)",
            "Incidence rate",
            "Rate",
            "Age-standardised incidence rate (per 100,000)",
        ],
    )
    cases_col = find_column(
        df,
        [
            "Number",
            "Cases",
            "Count",
            "Number of cases",
            "Incidence count",
        ],
    )

    if rate_col is None and cases_col is None:
        raise ValueError(
            "Could not find a usable numeric column. Need either a rate column or a cases/count column."
        )

    renamed = pd.DataFrame()

    if state_col:
        renamed["state"] = df[state_col].astype(str).str.strip()
    if year_col:
        renamed["year"] = pd.to_numeric(df[year_col], errors="coerce")
    if sex_col:
        renamed["sex"] = df[sex_col].astype(str).str.strip()
    if age_col:
        renamed["age_group"] = df[age_col].astype(str).str.strip()
    if cancer_col:
        renamed["cancer_group"] = df[cancer_col].astype(str).str.strip()
    if rate_col:
        renamed["incidence_rate"] = pd.to_numeric(df[rate_col], errors="coerce")
    if cases_col:
        renamed["cases"] = pd.to_numeric(df[cases_col], errors="coerce")

    renamed = renamed.dropna(how="all")

    object_like_cols = renamed.select_dtypes(include=["object", "string"]).columns
    for col in object_like_cols:
        renamed[col] = renamed[col].replace(
            {
                "NULL": pd.NA,
                "null": pd.NA,
                "": pd.NA,
                ".": pd.NA,
                "..": pd.NA,
                "n.a.": pd.NA,
                "na": pd.NA,
            }
        )

    return renamed


def choose_metric_column(df: pd.DataFrame) -> str:
    if "incidence_rate" in df.columns and df["incidence_rate"].notna().any():
        return "incidence_rate"
    if "cases" in df.columns and df["cases"].notna().any():
        return "cases"
    raise ValueError("No usable metric column found after cleaning.")


def save_csv(df: pd.DataFrame, output_path: Path) -> None:
    df.to_csv(output_path, index=False, encoding="utf-8-sig")


def prepare_state_hover_data(df: pd.DataFrame, metric_col: str) -> pd.DataFrame:
    out = (
        df.dropna(subset=["state", metric_col])
        .groupby("state", as_index=False)[metric_col]
        .mean()
        .rename(columns={metric_col: "value"})
    )
    out["value"] = out["value"].round(2)
    return out.sort_values("state").reset_index(drop=True)


def prepare_state_comparison_data(df: pd.DataFrame, metric_col: str) -> pd.DataFrame:
    out = (
        df.dropna(subset=["state", metric_col])
        .groupby("state", as_index=False)[metric_col]
        .mean()
        .rename(columns={metric_col: "value"})
    )
    out["value"] = out["value"].round(2)
    return out.sort_values("value", ascending=False).reset_index(drop=True)


def prepare_age_distribution_data(df: pd.DataFrame, metric_col: str) -> pd.DataFrame:
    out = (
        df.dropna(subset=["age_group", metric_col])
        .groupby("age_group", as_index=False)[metric_col]
        .mean()
        .rename(columns={metric_col: "value"})
    )
    out["value"] = out["value"].round(2)

    def age_sort_key(value: str) -> tuple[int, str]:
        text = str(value)
        if text.lower() in {"all ages", "all ages combined"}:
            return (999, text)
        if text.startswith("90"):
            return (90, text)
        digits = "".join(ch if ch.isdigit() else " " for ch in text).split()
        if digits:
            return (int(digits[0]), text)
        return (998, text)

    return out.sort_values(by="age_group", key=lambda s: s.map(age_sort_key)).reset_index(drop=True)


def prepare_cancer_trend_data(df: pd.DataFrame, metric_col: str) -> pd.DataFrame:
    out = (
        df.dropna(subset=["year", metric_col])
        .groupby("year", as_index=False)[metric_col]
        .mean()
        .rename(columns={metric_col: "value"})
    )
    out["year"] = out["year"].astype(int)
    out["value"] = out["value"].round(2)
    return out.sort_values("year").reset_index(drop=True)


def prepare_gender_distribution_data(df: pd.DataFrame, metric_col: str) -> pd.DataFrame:
    filtered = df.dropna(subset=["sex", metric_col]).copy()
    out = (
        filtered.groupby("sex", as_index=False)[metric_col]
        .mean()
        .rename(columns={metric_col: "value"})
    )
    out["value"] = out["value"].round(2)
    return out.sort_values("value", ascending=False).reset_index(drop=True)


def prepare_year_state_data(df: pd.DataFrame, metric_col: str) -> pd.DataFrame:
    out = (
        df.dropna(subset=["year", "state", metric_col])
        .groupby(["year", "state"], as_index=False)[metric_col]
        .mean()
        .rename(columns={metric_col: "value"})
    )
    out["year"] = out["year"].astype(int)
    out["value"] = out["value"].round(2)
    return out.sort_values(["year", "state"]).reset_index(drop=True)


def try_create_state_outputs(
    base_df: pd.DataFrame,
    metric_col: str,
    output_dir: Path,
    created_files: list[str],
    skipped_files: list[str],
) -> None:
    if "state" not in base_df.columns:
        skipped_files.append("state_hover_data.csv (state column not found)")
        skipped_files.append("state_comparison.csv (state column not found)")
        return

    state_hover_df = prepare_state_hover_data(base_df, metric_col)
    state_hover_path = output_dir / "state_hover_data.csv"
    save_csv(state_hover_df, state_hover_path)
    created_files.append(str(state_hover_path))

    state_comparison_df = prepare_state_comparison_data(base_df, metric_col)
    state_comparison_path = output_dir / "state_comparison.csv"
    save_csv(state_comparison_df, state_comparison_path)
    created_files.append(str(state_comparison_path))


def try_create_age_output(
    base_df: pd.DataFrame,
    metric_col: str,
    output_dir: Path,
    created_files: list[str],
    skipped_files: list[str],
) -> None:
    if "age_group" not in base_df.columns:
        skipped_files.append("age_distribution.csv (age_group column not found)")
        return

    age_distribution_df = prepare_age_distribution_data(base_df, metric_col)
    age_distribution_path = output_dir / "age_distribution.csv"
    save_csv(age_distribution_df, age_distribution_path)
    created_files.append(str(age_distribution_path))


def try_create_trend_output(
    base_df: pd.DataFrame,
    metric_col: str,
    output_dir: Path,
    created_files: list[str],
    skipped_files: list[str],
) -> None:
    if "year" not in base_df.columns:
        skipped_files.append("cancer_trend.csv (year column not found)")
        return

    cancer_trend_df = prepare_cancer_trend_data(base_df, metric_col)
    cancer_trend_path = output_dir / "cancer_trend.csv"
    save_csv(cancer_trend_df, cancer_trend_path)
    created_files.append(str(cancer_trend_path))


def try_create_gender_output(
    base_df: pd.DataFrame,
    metric_col: str,
    output_dir: Path,
    created_files: list[str],
    skipped_files: list[str],
) -> None:
    if "sex" not in base_df.columns:
        skipped_files.append("gender_distribution.csv (sex column not found)")
        return

    gender_distribution_df = prepare_gender_distribution_data(base_df, metric_col)
    if gender_distribution_df.empty:
        skipped_files.append("gender_distribution.csv (no usable gender data)")
        return

    gender_distribution_path = output_dir / "gender_distribution.csv"
    save_csv(gender_distribution_df, gender_distribution_path)
    created_files.append(str(gender_distribution_path))


def try_create_year_state_output(
    base_df: pd.DataFrame,
    metric_col: str,
    output_dir: Path,
    created_files: list[str],
    skipped_files: list[str],
) -> None:
    if "year" not in base_df.columns or "state" not in base_df.columns:
        skipped_files.append("year_state_comparison.csv (year or state column not found)")
        return

    year_state_df = prepare_year_state_data(base_df, metric_col)
    if year_state_df.empty:
        skipped_files.append("year_state_comparison.csv (no usable year-state data)")
        return

    year_state_path = output_dir / "year_state_comparison.csv"
    save_csv(year_state_df, year_state_path)
    created_files.append(str(year_state_path))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare frontend-ready CSV datasets for map hover, charts, and trend analysis."
    )
    parser.add_argument(
        "--input-file",
        default=DEFAULT_INPUT_FILE,
        help=f"Path to cleaned melanoma dataset. Default: {DEFAULT_INPUT_FILE}",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to save processed frontend files. Default: {DEFAULT_OUTPUT_DIR}",
    )
    args = parser.parse_args()

    input_file = Path(args.input_file)
    output_dir = Path(args.output_dir)
    ensure_output_dir(output_dir)

    raw_df = load_dataset(input_file)
    base_df = prepare_base_dataframe(raw_df)
    metric_col = choose_metric_column(base_df)

    created_files: list[str] = []
    skipped_files: list[str] = []

    try_create_state_outputs(base_df, metric_col, output_dir, created_files, skipped_files)
    try_create_age_output(base_df, metric_col, output_dir, created_files, skipped_files)
    try_create_trend_output(base_df, metric_col, output_dir, created_files, skipped_files)
    try_create_gender_output(base_df, metric_col, output_dir, created_files, skipped_files)
    try_create_year_state_output(base_df, metric_col, output_dir, created_files, skipped_files)

    print("Frontend dataset preparation completed.")
    print(f"Metric used for aggregation: {metric_col}")

    if created_files:
        print("\nCreated files:")
        for path in created_files:
            print(f"  - {path}")

    if skipped_files:
        print("\nSkipped files:")
        for item in skipped_files:
            print(f"  - {item}")


if __name__ == "__main__":
    main()