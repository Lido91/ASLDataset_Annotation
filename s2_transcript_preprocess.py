import os
import csv
import json
import re

from conf import *

import re


def clean_text(text):
    replacements = {
        '\u201c': '"',
        '\u201d': '"',
        '\u2014': '-',
        '\u2018': "'",
        '\u2019': "'",
        '\u2026': '...',
        '\n': ' ',
        '\r': ' ',
    }

    pattern = re.compile("|".join(map(re.escape, replacements.keys())))
    text = pattern.sub(lambda x: replacements[x.group()], text)

    text = re.sub(r'[^\x00-\x7F]+', '', text)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\s+', ' ', text)

    return text.lower().strip()


def load_transcript_from_json(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        transcript_data = json.load(file)
    return transcript_data

def split_captions(transcript_list, file_name, interval=100):
    result = []
    segment_start = 0
    segment_index = -1

    filtered_transcripts = [t for t in transcript_list if 'text' in t and 'start' in t]
    if not filtered_transcripts:
        print(f"No valid transcripts for video {file_name}")
        return result

    caption_list = [t["text"] for t in filtered_transcripts]
    start_list = [t['start'] for t in filtered_transcripts]

    while segment_start < start_list[-1]:
        condition = lambda x, start, length: start <= x < start + length
        seg_caption_list = [
            caption_list[i]
            for i in range(len(caption_list))
            if condition(start_list[i], segment_start, interval)
        ]
        segment_text = " ".join(seg_caption_list)
        segment_text = clean_text(segment_text)

        # Move to the next segment
        segment_start += interval * (3 / 4)
        segment_index += 1

        if not segment_text:
            continue

        sentence_name = f"{file_name}-{segment_index:03d}"
        result.append({"SENTENCE_NAME": sentence_name, "SENTENCE": segment_text})

        if caption_list[-1] in seg_caption_list:
            break

    return result

import pandas as pd
import csv  # For specifying quoting options

def store_to_csv(video_data, csv_path):
    # Convert the video data (list of dictionaries) to a DataFrame
    df = pd.DataFrame(video_data)

    # Write to CSV with quoting
    if os.path.exists(csv_path):
        df.to_csv(csv_path, mode='a', header=False, index=False, encoding='utf-8', quoting=csv.QUOTE_ALL)
    else:
        df.to_csv(csv_path, mode='w', header=True, index=False, encoding='utf-8', quoting=csv.QUOTE_ALL)


with open(ids_list, 'r', encoding='utf-8') as file:
    video_ids = [line.strip() for line in file if line.strip()]

print(f"Processing {len(video_ids)} videos.")

for video_id in video_ids:
    try:
        json_file = os.path.join(transcript_dir, f"{video_id}.json")
        if not os.path.exists(json_file):
            continue

        transcript_list = load_transcript_from_json(json_file)
        if not transcript_list:
            continue

        split_segments = split_captions(transcript_list, video_id)
        if split_segments:
            store_to_csv(split_segments, csv_path)

    except Exception as e:
        print(f"Error processing {video_id}: {e}")
        continue

