from yt_dlp import YoutubeDL
import csv
import os
import time
from glob import glob

from conf import *  # Keeping 'conf' as requested


def get_downloaded_video_ids(directory):
    """
    Retrieves a list of video IDs from existing MP4 files in the specified directory.

    Args:
        directory (str): Path to the directory containing video files

    Returns:
        list: List of video IDs extracted from filenames without extensions
    """
    video_files = glob(os.path.join(directory, "*.mp4"))
    return [os.path.splitext(os.path.basename(file))[0] for file in video_files]


previously_downloaded_ids = get_downloaded_video_ids(OUTPUT_DIR)

# Read video IDs from input file
with open(ID, "r") as file:
    target_video_ids = [line.strip() for line in file.readlines() if line.strip()]

# Create output directory if it doesn't exist
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# YouTube download configuration
download_options = {
    # Video quality settings
    "format": "worstvideo[height>=720]/bestvideo[height<=480]",
    "writesubtitles": False,
    "outtmpl": f"{VIDEO_DIR}/%(id)s.%(ext)s",
    # Performance optimizations
    "nocheckcertificate": True,
    "noplaylist": True,
    "no-metadata-json": True,
    "no-metadata": True,
    "concurrent-fragments": 3,  # Parallel fragment downloads
    "hls-prefer-ffmpeg": True,  # Faster HLS processing
    "http-chunk-size": 10485760,  # 10MB chunks for efficient downloads
    "sleep-interval": 0,
    "geo-bypass": True,
    # Rate limiting to prevent throttling
    "limit_rate": "5M",
}


def process_youtube_video(video_dir, output_dir, video_id):
    """
    Downloads a YouTube video using specified parameters and extracts video information.

    Args:
        video_dir (str): Directory for temporary video storage
        output_dir (str): Directory for final video output
        video_id (str): YouTube video identifier

    Returns:
        dict: Video information extracted by yt-dlp
    """
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    with YoutubeDL(download_options) as yt:
        return yt.extract_info(video_url)


# Process videos while skipping already downloaded ones
video_data = []
for video_id in target_video_ids:
    if video_id not in previously_downloaded_ids:
        time.sleep(2)  # Rate limiting pause
        try:
            process_youtube_video(VIDEO_DIR, OUTPUT_DIR, video_id)
        except:
            continue
    else:
        print(f"Video {video_id} already downloaded")
        continue
