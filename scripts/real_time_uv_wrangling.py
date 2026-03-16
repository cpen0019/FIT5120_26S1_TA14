from __future__ import annotations

import argparse
import csv
from pathlib import Path

from uv_service import get_citywise_uv, get_hourly_forecast, get_realtime_uv, get_weekly_forecast


DEFAULT_OUTPUT_DIR = "filtered_datasets"
DEFAULT_POSTCODE = "3000"


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return

    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def export_uv_datasets(
    postcode: str = DEFAULT_POSTCODE,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    file_prefix: str = "open_meteo_uv",
) -> dict[str, str]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    realtime = [get_realtime_uv(postcode=postcode)]
    hourly = get_hourly_forecast(postcode=postcode)
    weekly = get_weekly_forecast(postcode=postcode)
    citywise = get_citywise_uv()

    saved_files: dict[str, str] = {}
    datasets = {
        "realtime": realtime,
        "hourly": hourly,
        "weekly": weekly,
        "citywise": citywise,
    }
    for dataset_name, rows in datasets.items():
        csv_path = output_path / f"{file_prefix}_{dataset_name}.csv"
        write_csv(csv_path, rows)
        saved_files[dataset_name] = str(csv_path)

    return saved_files


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch postcode-based UV data and save it as CSV files.")
    parser.add_argument("--postcode", default=DEFAULT_POSTCODE)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--file-prefix", default="open_meteo_uv")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    saved_files = export_uv_datasets(
        postcode=args.postcode,
        output_dir=args.output_dir,
        file_prefix=args.file_prefix,
    )
    print("Saved UV CSV files:")
    for dataset_name, file_path in saved_files.items():
        print(f"  - {dataset_name}: {file_path}")


if __name__ == "__main__":
    main()
