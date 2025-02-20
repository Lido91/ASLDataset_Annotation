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
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api import CouldNotRetrieveTranscript, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable, TooManyRequests
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


def download_transcripts():
    """Download transcripts for video IDs in conf.ID if not already saved."""
    os.makedirs(c.TRANSCRIPT_DIR, exist_ok=True)
    existing_ids = get_existing_ids(c.TRANSCRIPT_DIR, "json")

    # Read target video IDs and remove those already downloaded
    with open(c.ID, "r", encoding="utf-8") as f:
        all_ids = {line.strip() for line in f if line.strip()}

    ids = all_ids - existing_ids

    if not ids:
        logger.info("All transcripts are already downloaded.")
        return

    formatter = JSONFormatter()
    sleep_time = 0.2

    # Use a progress bar to show download progress
    for video_id in tqdm(list(ids), desc="Downloading transcripts"):
        try:
            time.sleep(sleep_time)  # Rate limiting pause
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=c.LANGUAGE)
            json_transcript = formatter.format_transcript(transcript)
            transcript_path = os.path.join(c.TRANSCRIPT_DIR, f"{video_id}.json")
            with open(transcript_path, "w", encoding="utf-8") as out_file:
                out_file.write(json_transcript)
            logger.info("SUCCESS: Transcript for %s saved.", video_id)
        except CouldNotRetrieveTranscript as e:
            logger.error("Could not retrieve transcript for %s. Error: %s", video_id, e)
        except TranscriptsDisabled as e:
            logger.error("Transcripts are disabled for %s. Error: %s", video_id, e)
        except NoTranscriptFound as e:
            logger.error("No transcript found for %s in the specified languages. Error: %s", video_id, e)
        except VideoUnavailable as e:
            logger.error("Video %s is unavailable. Error: %s", video_id, e)
        except TooManyRequests as e:
            sleep_time += 0.2  # Slightly increase delay on error
            logger.error("Too many requests for %s. Error: %s", video_id, e)
        except Exception as e:
            logger.error("An unexpected error occurred for %s. Error: %s", video_id, e)


def process_youtube_video(video_id, download_options):
    """Download a YouTube video using specified options."""
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        with YoutubeDL(download_options) as yt:
            yt.extract_info(video_url)
        logger.info("SUCCESS: Video %s downloaded.", video_id)
    except Exception as e:
        logger.error("FAILED: Video %s download failed. Error: %s", video_id, e)


def download_videos():
    """Download videos for video IDs specified in conf.ID if not already downloaded."""
    os.makedirs(c.OUTPUT_DIR, exist_ok=True)
    os.makedirs(c.VIDEO_DIR, exist_ok=True)
    existing_ids = get_existing_ids(c.OUTPUT_DIR, "mp4")

    with open(c.ID, "r", encoding="utf-8") as f:
        all_ids = {line.strip() for line in f if line.strip()}

    ids = all_ids - existing_ids

    for video_id in ids:
        time.sleep(1)  # Rate limiting pause
        process_youtube_video(video_id, download_options)


# Global YouTube download configuration
download_options = {
    "format": "worstvideo[height>=720]/bestvideo[height<=480]",
    "writesubtitles": False,
    "outtmpl": os.path.join(c.VIDEO_DIR, "%(id)s.%(ext)s"),
    "nocheckcertificate": True,
    "noplaylist": True,
    "no-metadata-json": True,
    "no-metadata": True,
    "concurrent-fragments": 5,
    "hls-prefer-ffmpeg": True,
    "http-chunk-size": 10485760,  # 10MB chunks
    "sleep-interval": 0,
    "geo-bypass": True,
    "limit_rate": "5M",
}


def main():
    logger.info("Starting transcript download...")
    download_transcripts()
    logger.info("Transcript download completed.\n")

    logger.info("Starting video download...")
    download_videos()
    logger.info("Video download completed.")


if __name__ == "__main__":
    main()
