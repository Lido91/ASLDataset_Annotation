import os
import re
import subprocess
from glob import glob
from typing import Dict, List, Optional

import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
import logging

import conf as c

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def find_video_files(directory: str) -> List[str]:
    """
    Find all .mp4 files in the specified directory and return their base names without extension.
    """
    pattern = os.path.join(directory, '*.mp4')
    files = glob(pattern)
    base_names = [os.path.splitext(os.path.basename(file))[0] for file in files]
    logger.debug(f"Found video files: {base_names}")
    return base_names


def load_transcript(csv_file: str) -> Dict[str, List[float]]:
    """
    Load the CSV file and return a dictionary mapping SENTENCE_NAME to [START, END].
    """
    try:
        # Read the CSV file into a DataFrame
        data = pd.read_csv(csv_file, delimiter=',', on_bad_lines='skip')

        # Extract the relevant columns: SENTENCE_NAME, START, END
        df = data[['SENTENCE_NAME', 'START', 'END']].dropna()

        # Create a dictionary with SENTENCE_NAME as key and [START, END] as value
        transcript_dict = df.set_index('SENTENCE_NAME')[['START', 'END']].apply(lambda row: [row['START'], row['END']], axis=1).to_dict()

        # Debug logging the loaded data
        logger.debug(f"Loaded transcript data: {transcript_dict}")

        return transcript_dict
    except Exception as e:
        logger.error(f"Error loading CSV file {csv_file}: {e}")
        return {}


def convert_to_10fps(
    video_file: str,
    output_file: str,
    start_time: Optional[float] = None,
    duration: Optional[float] = None,
    use_gpu: bool = True
) -> None:
    """
    Convert a segment of the video to 10 fps using ffmpeg.
    """
    command = ['ffmpeg']

    # Add hardware-accelerated decoding if GPU is used
    if use_gpu:
        command += ['-hwaccel', 'cuda', '-hwaccel_output_format', 'cuda']

    if start_time is not None:
        command += ['-ss', str(start_time)]

    if duration is not None:
        command += ['-t', str(duration)]

    command += ['-i', video_file, '-y']  # Overwrite output file if exists

    # Video filter for frame rate
    command += ['-filter:v', 'fps=10']

    # Codec selection
    if use_gpu:
        command += [
            '-c:v', 'av1_nvenc',
            '-cq:v', '30',
            '-b:v', '400k',
            '-maxrate', '60k',
            '-bufsize', '800k',
            '-preset', 'p7'
        ]
    else:
        command += [
            '-c:v', 'libx264',
            '-qp', '20'
        ]

    # Disable audio
    command += ['-an', output_file]

    logger.debug(f"Running ffmpeg command: {' '.join(command)}")
    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        logger.info(f"Converted to 10 fps: {output_file}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to convert {video_file} to 10 fps: {e.stderr.decode().strip()}")


def get_video_duration(video_path: str) -> Optional[float]:
    """
    Get the duration of the video in seconds using ffmpeg.
    """
    command = ['ffmpeg', '-i', video_path]
    try:
        result = subprocess.run(
            command,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            check=False
        )
        duration_match = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", result.stderr)
        if duration_match:
            hours, minutes, seconds = map(float, duration_match.groups())
            duration_in_seconds = hours * 3600 + minutes * 60 + seconds
            logger.debug(f"Duration of {video_path}: {duration_in_seconds} seconds")
            return duration_in_seconds
        else:
            logger.warning(f"Could not determine duration for video: {video_path}")
            return None
    except Exception as e:
        logger.error(f"Error getting duration for {video_path}: {e}")
        return None


def process_segment(
    file_name: str,
    video_dir: str,
    output_dir: str,
    sentence_time_dict: Dict[str, List[float]],
    use_gpu: bool = True
) -> None:
    """
    Process a single video file by splitting it into segments and converting each to 10 fps.
    """
    video_path = os.path.join(video_dir, f"{file_name}.mp4")
    video_duration = get_video_duration(video_path)

    if video_duration is None:
        logger.warning(f"Skipping file due to unknown duration: {video_path}")
        return

    for sentence_name, times in sentence_time_dict.items():
        if not sentence_name.startswith(f"{file_name}-"):
            continue  # Skip unrelated sentences

        start_time, end_time = times
        duration = end_time - start_time

        output_path = os.path.join(output_dir, f"{sentence_name}.mp4")

        if os.path.exists(output_path):
            logger.info(f"Output file already exists. Skipping: {output_path}")
            continue

        convert_to_10fps(
            video_file=video_path,
            output_file=output_path,
            start_time=start_time,
            duration=duration,
            use_gpu=use_gpu
        )

    logger.info(f"Completed processing for video: {file_name}")


def main():
    # Load video files and transcript
    video_files = find_video_files(c.VIDEO_DIR)
    sentence_time_dict = load_transcript(c.CSV_FILE)

    if not video_files:
        logger.error("No video files found to process.")
        return

    if not sentence_time_dict:
        logger.error("No transcript data loaded. Exiting.")
        return

    # Ensure output directory exists
    os.makedirs(c.OUTPUT_DIR, exist_ok=True)

    logger.info(f"Starting processing of {len(video_files)} video files.")

    # Use ProcessPoolExecutor for multiprocessing
    with ProcessPoolExecutor(max_workers=c.MAX_WORKERS) as executor:
        # Submit all video processing tasks
        futures = [
            executor.submit(
                process_segment,
                file_name,
                c.VIDEO_DIR,
                c.OUTPUT_DIR,
                sentence_time_dict,
                c.USE_GPU
            ) for file_name in video_files
        ]

        # Monitor progress
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                logger.error(f"Processing generated an exception: {exc}")

    logger.info("All video processing tasks completed.")


if __name__ == "__main__":
    main()
