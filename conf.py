import os

# gpu setting
USE_GPU = True

# how2sign dataset
H2S_VIDEO_DIR = "dataset/how2sign/"
H2S_OUTPUT_DIR = "dataset/how2sign/npy/"

# youtube asl dataset
ROOT = os.path.dirname(os.path.abspath(__file__))
ID = "youtube-asl_youtube_asl_video_ids.txt"
VIDEO_DIR = f"{ROOT}/dataset/origin/"
OUTPUT_DIR = f"{ROOT}/dataset/npy/"
TRANSCRIPT_DIR = f"{ROOT}/dataset/transcript/"
CSV_FILE = f"video_info.csv"
MAX_FRAME = 512
DURATION = 16
OVERLAP = 4
MAX_WORKERS = 8
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


