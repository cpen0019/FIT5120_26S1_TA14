from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

WRANGLING_SCRIPT = PROJECT_ROOT / "cancer_data_wrangling.py"
FRONTEND_SCRIPT = PROJECT_ROOT / "prepare_frontend_data.py"
ANALYTICS_SCRIPT = PROJECT_ROOT / "cancer_analytics.py"

DEFAULT_CANCER_GROUP = "Melanoma of the skin"
DEFAULT_OUTPUT_DIR = "filtered_datasets"


def run_step(command: list[str], step_name: str) -> None:
    print(f"\n{'=' * 70}")
    print(f"Running: {step_name}")
    print(f"Command: {' '.join(command)}")
    print(f"{'=' * 70}\n")

    result = subprocess.run(command, cwd=PROJECT_ROOT)

    if result.returncode != 0:
        raise RuntimeError(f"{step_name} failed with exit code {result.returncode}")

    print(f"\nCompleted: {step_name}\n")


def validate_required_files() -> None:
    missing_files = []

    for file_path in [WRANGLING_SCRIPT, FRONTEND_SCRIPT, ANALYTICS_SCRIPT]:
        if not file_path.exists():
            missing_files.append(str(file_path.name))

    if missing_files:
        raise FileNotFoundError(
            "Missing required script files:\n" + "\n".join(f"- {name}" for name in missing_files)
        )


def main() -> None:
    validate_required_files()

    python_executable = sys.executable

    # Step 1: Wrangle raw cancer workbooks into filtered CSV files
    wrangling_command = [
        python_executable,
        str(WRANGLING_SCRIPT),
        "--cancer-group",
        DEFAULT_CANCER_GROUP,
        "--output-dir",
        DEFAULT_OUTPUT_DIR,
    ]

    # Step 2: Prepare frontend-ready processed files
    frontend_command = [
        python_executable,
        str(FRONTEND_SCRIPT),
    ]

    # Step 3: Prepare master cancer analytics dataset
    analytics_command = [
        python_executable,
        str(ANALYTICS_SCRIPT),
    ]

    try:
        run_step(wrangling_command, "Cancer data wrangling")
        run_step(frontend_command, "Frontend dataset preparation")
        run_step(analytics_command, "Cancer analytics dataset preparation")

        print(f"\n{'=' * 70}")
        print("Pipeline completed successfully.")
        print("Generated outputs should now be available in:")
        print("- filtered_datasets/")
        print("- processed/")
        print(f"{'=' * 70}\n")

    except Exception as exc:
        print(f"\nPipeline failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()