"""Utility helpers for recording existing video IDs in the dataset."""
import logging
import os
from glob import glob

import conf as c

logger = logging.getLogger(__name__)

EXISTING_VIDEO_IDS_FILE = os.path.join(c.ROOT, "existing_video_ids.txt")


def _discover_video_ids(directory=c.VIDEO_DIR, extension="mp4"):
    pattern = os.path.join(directory, f"*.{extension}")
    files = glob(pattern)
    return sorted(os.path.splitext(os.path.basename(path))[0] for path in files)


def write_existing_video_ids(
    output_path=EXISTING_VIDEO_IDS_FILE,
    extension="mp4",
    existing_ids=None,
):
    """Persist the IDs of downloaded videos and return them as a set."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if existing_ids is None:
        existing_ids = _discover_video_ids(extension=extension)
    else:
        existing_ids = sorted(existing_ids)
    with open(output_path, "w", encoding="utf-8") as out_file:
        out_file.write("# existing video ids recorded by existing_video_ids.py\n")
        out_file.write(f"# count={len(existing_ids)}\n")
        for video_id in existing_ids:
            out_file.write(f"{video_id}\n")
    logger.info("Recorded %d existing video IDs to %s", len(existing_ids), output_path)
    return set(existing_ids)


def load_existing_video_id_list(input_path=EXISTING_VIDEO_IDS_FILE):
    """Load the skip list of video IDs recorded in the text file."""
    if not os.path.exists(input_path):
        return set()
    with open(input_path, "r", encoding="utf-8") as in_file:
        return {
            line.strip()
            for line in in_file
            if line.strip() and not line.lstrip().startswith("#")
        }


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    write_existing_video_ids()
