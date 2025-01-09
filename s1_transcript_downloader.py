import time
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter
from glob import glob
import os
import conf as c  # Keeping original conf import name


def get_existing_transcripts(directory):
    """
    Retrieves a list of video IDs that already have transcripts saved.

    Args:
        directory (str): Path to the directory containing transcript files

    Returns:
        list: List of video IDs with existing transcripts (without file extensions)
    """
    transcript_files = glob(os.path.join(directory, "*.json"))
    return [os.path.splitext(os.path.basename(file))[0] for file in transcript_files]


previously_saved_transcripts = get_existing_transcripts(c.TRANSCRIPT_DIR)

# Read target video IDs from input file
with open(c.ID, "r") as file:
    target_video_ids = [line.strip() for line in file.readlines() if line.strip()]

# Initialize JSON formatter for transcript conversion
transcript_formatter = JSONFormatter()

# Process each video ID and save its transcript
for video_id in target_video_ids:
    if video_id not in previously_saved_transcripts:
        try:
            time.sleep(2)  # Rate limiting pause
            # Fetch transcript in specified language
            transcript_data = YouTubeTranscriptApi.get_transcript(
                video_id, languages=c.LANGUAGE
            )

            # Convert transcript to JSON format
            json_transcript = transcript_formatter.format_transcript(transcript_data)

            # Save formatted transcript to file
            transcript_path = f"{c.TRANSCRIPT_DIR}/{video_id}.json"
            with open(transcript_path, "w", encoding="utf-8") as json_file:
                json_file.write(json_transcript)

            print(f"SUCCESSFUL! {video_id} transcript saved successfully.")
        except Exception as e:
            print(f"FAILED! {video_id} transcript failed to be saved.")
            continue
    else:
        print(f"EXISTED! {video_id} is already saved.")
        continue
