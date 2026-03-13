from pathlib import Path
import pandas as pd


INPUT_FILE = "filtered_datasets/aihw-can-122-CDiA-2023-Book-7-Cancer-incidence-by-state-and-territory__melanoma_of_the_skin.csv"
OUTPUT_FILE = "processed/cancer_analytics.csv"


def find_column(df, candidates):
    normalized = {col.lower(): col for col in df.columns}

    for candidate in candidates:
        if candidate.lower() in normalized:
            return normalized[candidate.lower()]

    return None


def prepare_cancer_analytics():

    df = pd.read_csv(INPUT_FILE)

    # identify columns
    state_col = find_column(df, ["State", "State or Territory"])
    year_col = find_column(df, ["Year"])
    sex_col = find_column(df, ["Sex"])
    age_col = find_column(df, ["Age group (years)", "Age group"])
    cases_col = find_column(df, ["Cases", "Number", "Count"])
    rate_col = find_column(df, [
        "Age-standardised rate (per 100,000)",
        "Incidence rate",
        "Rate"
    ])

    analytics_df = pd.DataFrame()

    if state_col:
        analytics_df["state"] = df[state_col]

    if year_col:
        analytics_df["year"] = df[year_col]

    if sex_col:
        analytics_df["sex"] = df[sex_col]

    if age_col:
        analytics_df["age_group"] = df[age_col]

    if cases_col:
        analytics_df["cases"] = pd.to_numeric(df[cases_col], errors="coerce")

    if rate_col:
        analytics_df["incidence_rate"] = pd.to_numeric(df[rate_col], errors="coerce")

    analytics_df = analytics_df.dropna(how="all")

    Path("processed").mkdir(exist_ok=True)

    analytics_df.to_csv(OUTPUT_FILE, index=False)

    print("Cancer analytics dataset created:")
    print(OUTPUT_FILE)
    print()
    print(analytics_df.head())


if __name__ == "__main__":
    prepare_cancer_analytics()