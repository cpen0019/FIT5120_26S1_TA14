import argparse
import csv
import re
from pathlib import Path


ROW_PATTERN = re.compile(
    r"\('((?:''|[^'])*)',\s*'((?:''|[^'])*)',\s*'((?:''|[^'])*)',\s*(-?\d+(?:\.\d+)?),\s*(-?\d+(?:\.\d+)?)\)"
)


def _unescape_sql_string(value: str) -> str:
    return value.replace("''", "'")


def parse_postcodes(sql_text: str) -> list[dict[str, str | float]]:
    rows = []
    for match in ROW_PATTERN.finditer(sql_text):
        postcode, suburb, state, latitude, longitude = match.groups()
        rows.append(
            {
                "postcode": _unescape_sql_string(postcode),
                "suburb": _unescape_sql_string(suburb),
                "state": _unescape_sql_string(state),
                "latitude": float(latitude),
                "longitude": float(longitude),
            }
        )

    if not rows:
        raise ValueError("No postcode rows were found in the SQL file.")

    return rows


def write_csv(rows: list[dict[str, str | float]], output_path: Path) -> None:
    fieldnames = ["postcode", "suburb", "state", "latitude", "longitude"]
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert australian-postcodes.sql into a CSV file."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="australian-postcodes.sql",
        help="Path to the SQL file. Defaults to australian-postcodes.sql",
    )
    parser.add_argument(
        "output",
        nargs="?",
        default="australian-postcodes.csv",
        help="Path to the output CSV file. Defaults to australian-postcodes.csv",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    sql_text = input_path.read_text(encoding="utf-8")
    rows = parse_postcodes(sql_text)
    write_csv(rows, output_path)

    print(f"Wrote {len(rows)} rows to {output_path}")


if __name__ == "__main__":
    main()
