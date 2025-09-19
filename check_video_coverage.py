#!/usr/bin/env python3
"""Report dataset coverage between CSV entries and ID list."""
from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).parent
CSV_PATH = ROOT / "youtube_asl.csv"
IDS_PATH = ROOT / "youtube-asl_youtube_asl_video_ids.txt"


def load_csv_video_ids(csv_path: Path) -> set[str]:
    with csv_path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file, delimiter="\t")
        field = "VIDEO_NAME"
        if field not in reader.fieldnames:
            raise ValueError(f"Expected column '{field}' in {csv_path}")
        return {row[field].strip() for row in reader if row.get(field)}


def load_txt_ids(txt_path: Path) -> set[str]:
    with txt_path.open("r", encoding="utf-8") as txt_file:
        return {line.strip() for line in txt_file if line.strip()}


def main() -> None:
    csv_ids = load_csv_video_ids(CSV_PATH)
    txt_ids = load_txt_ids(IDS_PATH)

    missing_in_csv = sorted(txt_ids - csv_ids)
    extra_in_csv = sorted(csv_ids - txt_ids)

    print(f"CSV unique video names: {len(csv_ids)}")
    print(f"TXT video IDs: {len(txt_ids)}")

    if missing_in_csv:
        print(f"IDs listed in TXT but missing from CSV ({len(missing_in_csv)}):")
        for vid in missing_in_csv:
            print(f"  {vid}")
    else:
        print("No IDs missing from CSV.")

    if extra_in_csv:
        print(f"IDs present in CSV but not in TXT ({len(extra_in_csv)}):")
        for vid in extra_in_csv:
            print(f"  {vid}")
    else:
        print("No extra IDs in CSV.")


if __name__ == "__main__":  # pragma: no cover
    main()

