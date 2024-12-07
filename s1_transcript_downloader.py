import time
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter
from glob import glob
import os
import conf as c


def find_files(directory):
    files = glob(os.path.join(directory, "*.json"))
    return [os.path.splitext(os.path.basename(file))[0] for file in files]


saved_ids = find_files(c.TRANSCRIPT_DIR)

with open(c.ID, "r") as file:
    video_ids = [line.strip() for line in file.readlines() if line.strip()]

formatter = JSONFormatter()

for video_id in video_ids:
    if video_id not in saved_ids:
        try:
            time.sleep(2)
            # Must be a single transcript.
            transcript = YouTubeTranscriptApi.get_transcript(
                video_id, languages=c.LANGUAGE
            )
            # .format_transcript(transcript) turns the transcript into a JSON string.
            json_formatted = formatter.format_transcript(transcript)

            # Now we can write it out to a file.
            with open(
                f"{c.TRANSCRIPT_DIR}/{video_id}.json", "w", encoding="utf-8"
            ) as json_file:
                json_file.write(json_formatted)

            print(f"SUCCESSFUL! {video_id} transcript saved successfully.")
        except Exception as e:
            print(f"FAILED! {video_id} transcript failed to be saved.")
            continue
    else:
        print(f"EXISTED! {video_id} is already saved.")
        continue
