#!/usr/bin/env python3
"""
s1_data_downloader.py

This script downloads YouTube transcripts and videos for video IDs specified in conf.ID.
Transcripts are downloaded first (if not already saved) and then videos are downloaded
(if not already present). Logging is used to provide detailed debugging information.
"""

import os
import time
import logging
from glob import glob
from yt_dlp import YoutubeDL
from yt_dlp.utils import (
    DownloadError,
    ExtractorError,
    PostProcessingError,
    UnavailableVideoError,
)
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    TooManyRequests,
)
from youtube_transcript_api.formatters import JSONFormatter
from tqdm import tqdm

import conf as c  # Using 'c' for configuration

# Configure logging for debugging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_existing_ids(directory, ext):
    """Return a set of IDs from files with the specified extension in the directory."""
    files = glob(os.path.join(directory, f"*.{ext}"))
    return {os.path.splitext(os.path.basename(f))[0] for f in files}


def load_video_ids(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def download_single_transcript(video_id, formatter, sleep_time):
    """Download a single transcript for a video ID."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=c.LANGUAGE)
        json_transcript = formatter.format_transcript(transcript)
        transcript_path = os.path.join(c.TRANSCRIPT_DIR, f"{video_id}.json")
        with open(transcript_path, "w", encoding="utf-8") as out_file:
            out_file.write(json_transcript)
        logger.info("SUCCESS: Transcript for %s saved.", video_id)
        return True, sleep_time
    except TooManyRequests as e:
        sleep_time += 0.1  # Slightly increase delay on error
        logger.error("Too many requests for %s. Error: %s", video_id, e)
        return False, sleep_time
    except Exception as e:
        logger.error("An unexpected error occurred for %s. Error: %s", video_id, e)
        return False, sleep_time


def download_transcripts():
    """Download transcripts for video IDs in conf.ID if not already saved."""
    os.makedirs(c.TRANSCRIPT_DIR, exist_ok=True)
    existing_ids = get_existing_ids(c.TRANSCRIPT_DIR, "json")

    all_ids = load_video_ids(c.ID)
    ids = list(all_ids - existing_ids)

    if not ids:
        logger.info("All transcripts are already downloaded.")
        return

    formatter = JSONFormatter()
    sleep_time = 0.2
    error_count = 0

    # Use a progress bar to show download progress
    with tqdm(ids, desc="Downloading transcripts") as pbar:
        for video_id in pbar:
            sleep_time = min(sleep_time, 2)
            time.sleep(sleep_time)  # Rate limiting pause
            success, sleep_time = download_single_transcript(
                video_id, formatter, sleep_time
            )

            if not success:
                error_count += 1

            pbar.set_postfix(errors=error_count)


def download_single_video(video_id, download_options):
    """Download a YouTube video using specified options."""
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        with YoutubeDL(download_options) as yt:
            yt.extract_info(video_url)
        logger.info("SUCCESS: Video %s downloaded.", video_id)
        return True
    except (
        DownloadError,
        ExtractorError,
        PostProcessingError,
        UnavailableVideoError,
    ) as e:
        logger.error("Error downloading video %s. Error: %s", video_id, e)
        return False
    except Exception as e:
        logger.error("An unexpected error occurred for %s. Error: %s", video_id, e)
        return False


def download_videos():
    """Download videos for video IDs specified in conf.ID if not already downloaded."""
    os.makedirs(c.NPY_DIR, exist_ok=True)
    os.makedirs(c.VIDEO_DIR, exist_ok=True)
    existing_ids = get_existing_ids(c.NPY_DIR, "mp4")

    all_ids = load_video_ids(c.ID)
    ids = list(all_ids - existing_ids)

    if not ids:
        logger.info("All videos have already been downloaded.")
        return

    error_count = 0
    # Use tqdm progress bar to show progress
    with tqdm(ids, desc="Downloading videos", unit="video") as pbar:
        for video_id in pbar:
            time.sleep(0.2)  # Rate limiting pause
            success = download_single_video(video_id, c.YT_CONFIG)
            if not success:
                error_count += 1
            pbar.set_postfix(errors=error_count)

    logger.info("Video download completed: Total %d, Errors %d.", error_count)


def main():
    logger.info("Starting transcript download...")
    download_transcripts()
    logger.info("Transcript download completed.\n")

    logger.info("Starting video download...")
    download_videos()
    logger.info("Video download completed.")


if __name__ == "__main__":
    main()
