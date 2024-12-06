import os
import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
from glob import glob
from typing import Dict, List
import logging
from concurrent.futures import ProcessPoolExecutor

import conf as c

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def load_transcript(csv_file: str) -> Dict[str, List[float]]:
    """Load the CSV file and return a dictionary mapping SENTENCE_NAME to [START, END]."""
    try:
        df = pd.read_csv(csv_file, delimiter=',', on_bad_lines='skip')[['SENTENCE_NAME', 'START', 'END']].dropna()
        return df.set_index('SENTENCE_NAME')[['START', 'END']] \
                 .apply(lambda row: [row['START'], row['END']], axis=1).to_dict()
    except Exception as e:
        logger.error(f"Error loading CSV file {csv_file}: {e}")
        return {}

def find_video_files(directory: str) -> List[str]:
    """Find all .mp4 files in the specified directory and return base names without extension."""
    return [os.path.splitext(os.path.basename(f))[0] for f in glob(os.path.join(directory, '*.mp4'))]

mp_holistic = mp.solutions.holistic

def mediapipe_detection(image, model):
    return model.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

def extract_keypoints(results):
    def landmarks_to_np(landmarks, indices):
        return np.array([[landmarks[i].x, landmarks[i].y, landmarks[i].z] for i in indices]) if landmarks else np.zeros((len(indices), 3))

    pose = landmarks_to_np(getattr(results.pose_landmarks, 'landmark', None), c.POSE_IDX)
    lh = landmarks_to_np(getattr(results.left_hand_landmarks, 'landmark', None), c.HAND_IDX)
    rh = landmarks_to_np(getattr(results.right_hand_landmarks, 'landmark', None), c.HAND_IDX)
    face = landmarks_to_np(getattr(results.face_landmarks, 'landmark', None), c.FACE_IDX)

    return np.concatenate([pose.flatten(), face.flatten(), lh.flatten(), rh.flatten()])

def process_segment(video_path: str, start_time: float, end_time: float, output_file: str):
    """Process a video segment, extract holistic keypoints, and save as .npy."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Error opening video: {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_skip = 6 if fps > 60 else (4 if fps > 40 else (2 if fps > 20 else 1))

    start_frame, end_frame = int(start_time * fps), int(end_time * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    all_landmarks = []
    with mp_holistic.Holistic(model_complexity=1, refine_face_landmarks=True,
                              min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        current_frame = start_frame
        while current_frame <= end_frame:
            ret, frame = cap.read()
            if not ret:
                break
            if (current_frame - start_frame) % frame_skip == 0:
                results = mediapipe_detection(frame, holistic)
                all_landmarks.append(extract_keypoints(results))
            current_frame += 1

    cap.release()

    data_array = np.array(all_landmarks)
    if data_array.size > 0 and np.any(data_array):
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        np.save(output_file, data_array)
        logger.info(f"Saved landmarks to {output_file}")
    else:
        logger.info(f"No valid landmarks for segment {video_path}, not saving.")

def main():
    transcript_dict = load_transcript(c.CSV_FILE)
    available_videos = find_video_files(c.VIDEO_DIR)

    tasks = []
    for sentence_name_number, (start, end) in transcript_dict.items():
        sentence_name = sentence_name_number.split("-")[0]
        if sentence_name in available_videos:
            video_path = os.path.join(c.VIDEO_DIR, f"{sentence_name}.mp4")
            output_file = os.path.join(c.OUTPUT_DIR, f"{sentence_name_number}.npy")
            tasks.append((video_path, start, end, output_file))

    # Use multiple processors
    with ProcessPoolExecutor(max_workers=c.MAX_WORKERS) as executor:
        for video_path, start, end, output_file in tasks:
            executor.submit(process_segment, video_path, start, end, output_file)

if __name__ == "__main__":
    main()

