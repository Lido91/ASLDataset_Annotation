import os
import csv
import json
import re
import numpy as np
import pandas as pd

import conf as c


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

    # Replace specific unicode characters
    pattern = re.compile("|".join(map(re.escape, replacements)))
    text = pattern.sub(lambda match: replacements[match.group()], text)

    # Remove non-ASCII characters, content within brackets, and extra whitespace
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\s+', ' ', text)

    return text.lower().strip()


def load_transcript(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        return json.load(file)


def split_captions(transcripts, file_name, duration=c.DURATION, overlap=c.OVERLAP):
    result = []
    segment_start = 0
    segment_index = -1

    # Filter transcripts with required keys
    valid_transcripts = [t for t in transcripts if 'text' in t and 'start' in t]
    if not valid_transcripts:
        print(f"No valid transcripts for video {file_name}")
        return result

    last_start = valid_transcripts[-1]['start']

    while segment_start < last_start:
        segment_end = segment_start + duration
        seg_texts = []

        for t in valid_transcripts:
            if segment_start <= t['start'] < segment_start + duration:
                seg_texts.append(t["text"])
                segment_end = max(segment_end, t['start'] + t.get('duration', 0))

        cleaned_text = clean_text(" ".join(seg_texts))
        segment_start += duration - overlap
        segment_index += 1

        if not cleaned_text:
            continue

        sentence = {
            "SENTENCE_NAME": f"{file_name}-{segment_index:03d}",
            "START": segment_start - (duration - overlap),
            "END": float(np.ceil(segment_end)),
            "SENTENCE": cleaned_text
        }
        result.append(sentence)

        # Stop if the last transcript is included
        if valid_transcripts[-1]["text"] in seg_texts:
            break

    return result


def store_to_csv(video_data, csv_path):
    df = pd.DataFrame(video_data)
    mode = 'a' if os.path.exists(csv_path) else 'w'
    header = not os.path.exists(csv_path)

    df.to_csv(
        csv_path,
        mode=mode,
        header=header,
        index=False,
        encoding='utf-8',
        quoting=csv.QUOTE_ALL
    )


def main():
    with open(c.ID, 'r', encoding='utf-8') as file:
        video_ids = [line.strip() for line in file if line.strip()]

    print(f"Processing {len(video_ids)} videos.")

    for video_id in video_ids:
        try:
            json_file = os.path.join(c.TRANSCRIPT_DIR, f"{video_id}.json")
            if not os.path.exists(json_file):
                continue

            transcripts = load_transcript(json_file)
            if not transcripts:
                continue

            segments = split_captions(transcripts, video_id)
            if segments:
                store_to_csv(segments, c.CSV_FILE)

        except Exception as e:
            print(f"Error processing {video_id}: {e}")


if __name__ == "__main__":
    main()