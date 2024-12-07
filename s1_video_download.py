from yt_dlp import YoutubeDL
import csv
import os
import time
from glob import glob

from conf import *


def find_files(directory):
    files = glob(os.path.join(directory, "*.mp4"))
    return [os.path.splitext(os.path.basename(file))[0] for file in files]


saved_ids = find_files(OUTPUT_DIR)

with open(ID, "r") as file:
    video_ids = [line.strip() for line in file.readlines() if line.strip()]

# Ensure the output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Options to download video at 360p or higher and 10 fps or higher, along with subtitles
opts = {
    "format": "worstvideo[height>=720]/bestvideo[height<=480]",
    "writesubtitles": False,  # don't download subtitles
    "outtmpl": f"{VIDEO_DIR}/%(id)s.%(ext)s",  # Output template for video file
    # optimization options
    "nocheckcertificate": True,  # Avoid SSL certificate verification (optional)
    "noplaylist": True,  # Don't download playlist if the URL is a playlist
    "no-metadata-json": True,  # Skip writing metadata JSON files
    "no-metadata": True,  # Avoid downloading extra metadata
    "concurrent-fragments": 3,  # Download multiple video fragments at once (for fragmented videos)
    "hls-prefer-ffmpeg": True,  # Prefer using ffmpeg for HLS streams (often faster)
    "http-chunk-size": 10485760,  # Download in 10MB chunks to speed up large downloads
    "sleep-interval": 0,  # No waiting between requests
    "geo-bypass": True,  # Avoid geographic restrictions
    # prevent throttling
    "limit_rate": "5M",
}


# Function to download the video, get resolution and fps, and store captions in a variable
def download_video(video_dir, output_dir, video_id):
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    with YoutubeDL(opts) as yt:
        info = yt.extract_info(video_url)


# Loop through the list of video URLs and gather the information
video_data = []
for video_id in video_ids:
    if video_id not in saved_ids:
        time.sleep(2)
        try:
            download_video(VIDEO_DIR, OUTPUT_DIR, video_id)
        except:
            continue
    else:
        print(f"Video {video_id} already downloaded")
        continue
