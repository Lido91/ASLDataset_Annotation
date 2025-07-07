import os

# =============================================================================
# PROJECT PATHS AND CONFIGURATION
# =============================================================================

# Base paths
ROOT = os.path.dirname(os.path.abspath(__file__))
VIDEO_DIR = f"{ROOT}/dataset/origin/"
NPY_DIR = f"{ROOT}/dataset/npy/"
TRANSCRIPT_DIR = f"{ROOT}/dataset/transcript/"

# Dataset files
ID = "youtube-asl_youtube_asl_video_ids.txt"
CSV_FILE = f"youtube_asl.csv"

# =============================================================================
# PROCESSING CONFIGURATION
# =============================================================================

# Frame processing
FRAME_SKIP = 2  # Number of frames to skip when extracting frames from a video

# Threading
MAX_WORKERS = 4

# FPS reduction
TARGET_FPS = 8.0  # Target FPS for reduced landmark data

# Supported languages
LANGUAGE = [
    "en",
    "ase",
    "en-US",
    "en-CA",
    "en-GB",
    "en-AU",
    "en-NZ",
    "en-IN",
    "en-ZA",
    "en-IE",
    "en-SG",
    "en-PH",
    "en-NG",
    "en-PK",
    "en-JM",
]

# =============================================================================
# YOUTUBE DOWNLOADER CONFIGURATION
# =============================================================================

YT_CONFIG = {
    # Video quality and format
    "format": "worstvideo[height>=720]/bestvideo[height<=480]",
    "writesubtitles": False,
    "outtmpl": os.path.join(VIDEO_DIR, "%(id)s.%(ext)s"),
    
    # Connection and security
    "nocheckcertificate": True,
    "geo-bypass": True,
    "limit_rate": "5M",
    "http-chunk-size": 10485760,  # 10MB chunks
    
    # Playlist and metadata
    "noplaylist": True,
    "no-metadata-json": True,
    "no-metadata": True,
    
    # Performance optimization
    "concurrent-fragments": 5,
    "hls-prefer-ffmpeg": True,
    "sleep-interval": 0,
}

# =============================================================================
# MEDIAPIPE LANDMARK INDICES
# =============================================================================

# Hand landmarks (21 points)
HAND_IDX = list(range(21))

# Pose landmarks (key body points)
POSE_IDX = [11, 12, 13, 14, 23, 24]

# Face landmarks (key facial features)
FACE_IDX = [
    0, 4, 13, 14, 17, 33, 37, 39, 46, 52, 55, 61, 64, 81, 82, 93,
    133, 151, 152, 159, 172, 178, 181, 263, 269, 276, 282, 285, 291,
    294, 311, 323, 362, 386, 397, 468, 473
]


