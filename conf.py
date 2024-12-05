import os


USE_GPU = True


# video downloader
ROOT = os.path.dirname(os.path.abspath(__file__))
ID = 'youtube-asl_youtube_asl_video_ids.txt'
VIDEO_DIR = f'{ROOT}/dataset/origin/'
OUTPUT_DIR = f'{ROOT}/dataset/10fps/'
TRANSCRIPT_DIR = f'{ROOT}/dataset/transcript/'
# transcript_dir = f'{root}/dataset/test/'
CSV_FILE = f'video_info.csv'

DURATION = 16
OVERLAP = 4
MAX_WORKERS = 1
LANGUAGE = ['en', 'ase', 'en-US', 'en-CA', 'en-GB', 'en-AU', 'en-NZ', 'en-IN', 'en-ZA', 'en-IE', 'en-SG', 'en-PH', 'en-NG', 'en-PK', 'en-JM']