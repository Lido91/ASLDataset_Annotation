from glob import glob
import subprocess
import re
import os
import pandas as pd

from conf import *

def find_files(directory):
    files = glob(os.path.join(directory, '*.mp4'))
    return [os.path.splitext(os.path.basename(file))[0] for file in files]


def load_csv2dict(csv_file):
    data = pd.read_csv(csv_file, delimiter=',', on_bad_lines='skip')
    df = data[['SENTENCE_NAME', 'SENTENCE']]
    sentence_dict = pd.Series(df.SENTENCE.values, index=df.SENTENCE_NAME).to_dict()

    return sentence_dict

# Function to convert video to 10 fps using ffmpeg
def convert_to_10fps(video_file, output_file, start_time=None, duration=None, gpu=True):
    command = ['ffmpeg']
    # Add start time if provided
    if start_time is not None:
        command.extend(['-ss', str(start_time)])

    # Add duration if provided
    if duration is not None:
        command.extend(['-t', str(duration)])

    # Using ffmpeg to convert the frame rate
    if gpu:
        # Using ffmpeg to convert the frame rate
        command.extend(['-i', video_file,
                        '-y',  # Automatically overwrite the output file
                        '-filter:v', 'fps=fps=10',
                        '-c:v', 'av1_nvenc',
                        '-cq:v', '25',
                        '-an', output_file])
    else:
        command.extend(['-i', video_file,
                   '-y',  # Automatically overwrite the output file
                   '-filter:v', 'fps=fps=10',
                   '-c:v', 'libx264',
                   '-qp', '20',
                   '-an', output_file])

    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Converted to 10 fps: {video_file}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to convert {video_file} to 10 fps: {e}")


def get_video_duration(video_path):
    command = ['ffmpeg', '-i', video_path]
    result = subprocess.run(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    # Search for the duration in the ffmpeg output
    duration_regex = re.search(r"Duration: (\d+:\d+:\d+\.\d+)", result.stderr)
    if duration_regex:
        duration_str = duration_regex.group(1)
        # Split into hours, minutes, seconds
        h, m, s = map(float, duration_str.split(':'))
        # Convert the duration to seconds
        duration_in_seconds = h * 3600 + m * 60 + s
        return duration_in_seconds
    else:
        print(f"Failed to get duration for video: {video_path}")
        return None

# Constants
duration = 100  # segment duration in seconds

# Initialize variables
start = 0
index = 0

# Find video files
# video_files = find_files(transcript_dir)
video_files = find_files(video_dir)
transcript_key = load_csv2dict(csv_path).keys()
print(transcript_key)
# Iterate through transcript list
for file_name in video_files:
    video_path = os.path.join(video_dir, file_name + '.mp4')
    print(video_path)
    # Get video duration using a function like get_video_duration(video_path)
    video_duration = get_video_duration(video_path)

    while start < video_duration:
        # Ensure that `start` is within the video duration
        if start >= video_duration:
            break

        # Save the current segment
        output_name = f"{file_name}-{index:03d}"
        if output_name not in transcript_key:
            break

        output_path = os.path.join(output_dir, output_name + '.mp4')

        # Calculate the duration for the segment, ensuring it doesn't exceed video length
        segment_end = min(start + duration, video_duration)
        actual_segment_duration = segment_end - start

        # Convert the video to 10fps
        convert_to_10fps(video_path, output_path, start, actual_segment_duration)

        if segment_end == video_duration:
            break

        # Move to the next segment (3/4 overlap, i.e., move forward by 25 seconds)
        start += (duration * 3/4)
        index += 1

    start = 0
    index = 0