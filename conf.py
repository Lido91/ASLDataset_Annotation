import os

# video downloader
root = os.path.dirname(os.path.abspath(__file__))
ids_list = 'youtube-asl_youtube_asl_video_ids.txt'
video_dir = f'{root}/dataset/origin/'
output_dir = f'{root}/dataset/10fps/'
transcript_dir = f'{root}/dataset/transcript/'
# transcript_dir = f'{root}/dataset/test/'
csv_path = f'video_info.csv'

duration = 100