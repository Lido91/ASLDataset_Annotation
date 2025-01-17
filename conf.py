import os

# gpu setting
USE_GPU = True


# video parameters
LENGTH_BASED_MAX_FRAME = True
LENGTH_BASED_FRAME_SKIP = False
FRAME_SKIP = 2
MAX_FRAME = 512

# how2sign dataset
H2S_VIDEO_DIR = "dataset/how2sign/val_raw_videos/raw_videos"
H2S_OUTPUT_DIR = "dataset/how2sign/npy/"
H2S_CSV_FILE = "dataset/how2sign/how2sign_realigned_val.csv"

# youtube asl dataset
ROOT = os.path.dirname(os.path.abspath(__file__))
ID = "youtube-asl_youtube_asl_video_ids.txt"

VIDEO_DIR = f"{ROOT}/dataset/origin/"
OUTPUT_DIR = f"{ROOT}/dataset/npy/"
CSV_FILE = f"youtube_asl.csv"

TRANSCRIPT_DIR = f"{ROOT}/dataset/transcript/"
DURATION = 16
OVERLAP = 4
MAX_WORKERS = 2
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

# mediapipe landmark indices
HAND_IDX = list(range(21))
POSE_IDX = [11, 12, 13, 14, 23, 24]
FACE_IDX = [
    0, 4, 13, 14, 17, 33, 37, 39, 46, 52, 55, 61, 64, 81, 82, 93,
    133, 151, 152, 159, 172, 178, 181, 263, 269, 276, 282, 285, 291,
    294, 311, 323, 362, 386, 397, 468, 473
]


