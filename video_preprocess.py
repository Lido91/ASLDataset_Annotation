from glob import glob
import subprocess
import os
import pandas as pd

def find_files(directory):
    files = glob(os.path.join(directory, '*.mp4'))
    return [os.path.splitext(os.path.basename(file))[0] for file in files]

# Function to convert video to 1 fps and 1280x720 resolution using ffmpeg
def convert_to_1fps(video_file, output_file, gpu=True):
    command = ['ffmpeg']

    # Using ffmpeg to convert the frame rate and resolution
    if gpu:
        command.extend([
            '-i', video_file,
            '-y',  # Automatically overwrite the output file
            '-filter:v', 'fps=1,scale=1280:720',  # Set fps to 1 and resolution to 1280x720
            '-c:v', 'av1_nvenc',
            '-cq:v', '25',
            '-an', output_file
        ])
    else:
        command.extend([
            '-i', video_file,
            '-y',  # Automatically overwrite the output file
            '-filter:v', 'fps=1,scale=1280:720',  # Set fps to 1 and resolution to 1280x720
            '-c:v', 'libx264',
            '-qp', '22',
            '-an', output_file
        ])

    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Converted to 1 fps and resized to 1280x720: {video_file}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to convert {video_file}: {e}")

video_dir = input('Enter the directory containing video files: ')
output_dir = input('Enter the directory to save the converted videos: ')

# Find video files
video_files = find_files(video_dir)

# Iterate through each video file and convert it
for file_name in video_files:
    video_path = os.path.join(video_dir, file_name + '.av1')
    output_path = os.path.join(output_dir, file_name + '.av1')
    convert_to_1fps(video_path, output_path)
