import csv

from backend.db import get_connection
from backend.config import FILTERED_DIR


INCIDENCE_FILE = FILTERED_DIR / "aihw-can-122-CDiA-2023-Book-1a-Cancer-incidence-age-standardised-rates-5-year-age-groups__melanoma_of_the_skin.csv"
MORTALITY_FILE = FILTERED_DIR / "aihw-can-122-CDiA-2023-Book-2a-Cancer-mortality-and-age-standardised-rates-by-age-5-year-groups__melanoma_of_the_skin.csv"
STATE_FILE = FILTERED_DIR / "aihw-can-122-CDiA-2023-Book-7-Cancer-incidence-by-state-and-territory__melanoma_of_the_skin.csv"


def to_int(value):
    if value is None:
        return None
    value = str(value).strip()
    if value == "" or value.upper() == "NULL" or value in {"..", "np", "N/A"}:
        return None
    try:
        return int(float(value))
    except ValueError:
        return None


def to_float(value):
    if value is None:
        return None
    value = str(value).strip()
    if value == "" or value.upper() == "NULL" or value in {"..", "np", "N/A"}:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def import_incidence(conn):
    print(f"Opening: {INCIDENCE_FILE}")
    if not INCIDENCE_FILE.exists():
        print(f"Skipped: {INCIDENCE_FILE} not found")
        return

    inserted = 0
    with open(INCIDENCE_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        with conn.cursor() as cur:
            for row in reader:
                year = to_int(row.get("Year"))
                sex = row.get("Sex")
                age_group = row.get("Age group (years)")
                rate = to_float(row.get("Age-specific rate (per 100,000)"))

                if year is None or not sex or not age_group:
                    continue

                cur.execute(
                    """
                    INSERT INTO melanoma_incidence
                    (year, sex, age_group, age_specific_rate)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (year, sex, age_group, rate),
                )
                inserted += 1

    conn.commit()
    print(f"Imported melanoma_incidence: {inserted} rows")


def import_mortality(conn):
    print(f"Opening: {MORTALITY_FILE}")
    if not MORTALITY_FILE.exists():
        print(f"Skipped: {MORTALITY_FILE} not found")
        return

    inserted = 0
    with open(MORTALITY_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        with conn.cursor() as cur:
            for row in reader:
                year = to_int(row.get("Year"))
                sex = row.get("Sex")
                age_group = row.get("Age group (years)")
                rate = to_float(row.get("Age-specific rate (per 100,000)"))

                if year is None or not sex or not age_group:
                    continue

                cur.execute(
                    """
                    INSERT INTO melanoma_mortality
                    (year, sex, age_group, age_specific_rate)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (year, sex, age_group, rate),
                )
                inserted += 1

    conn.commit()
    print(f"Imported melanoma_mortality: {inserted} rows")


def import_state_incidence(conn):
    print(f"Opening: {STATE_FILE}")
    if not STATE_FILE.exists():
        print(f"Skipped: {STATE_FILE} not found")
        return

    inserted = 0
    with open(STATE_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        with conn.cursor() as cur:
            for row in reader:
                year = to_int(row.get("Year"))
                state = row.get("State or Territory")
                cases = to_int(row.get("Count"))
                rate = to_float(
                    row.get("Age-standardised rate 2001 Australian Standard Population  (per 100,000)")
                )

                if year is None or not state:
                    continue

                cur.execute(
                    """
                    INSERT INTO melanoma_state_incidence
                    (year, state, cases, age_standardised_rate)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (year, state, cases, rate),
                )
                inserted += 1

    conn.commit()
    print(f"Imported melanoma_state_incidence: {inserted} rows")


def main():
    print("Connecting to database...")
    conn = get_connection()
    print("Database connected.")

    try:
        import_incidence(conn)
        import_mortality(conn)
        import_state_incidence(conn)
        print("All CSV imports completed.")
    finally:
        conn.close()
        print("Database connection closed.")


if __name__ == "__main__":
    main()