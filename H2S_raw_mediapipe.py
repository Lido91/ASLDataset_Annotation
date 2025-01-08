import os
import cv2
import mediapipe as mp
import numpy as np
import logging
from glob import glob
from typing import List, Dict
from concurrent.futures import ProcessPoolExecutor
import pandas as pd

import conf as c

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

mp_holistic = mp.solutions.holistic


def load_transcript(csv_file: str) -> List[Dict]:
    """
    Load the CSV file and return a list of dictionaries containing
    VIDEO_NAME, SENTENCE_NAME, START_REALIGNED, and END_REALIGNED.
    """
    try:
        df = pd.read_csv(csv_file, delimiter="\t", on_bad_lines="skip")[
            ["VIDEO_NAME", "SENTENCE_NAME", "START_REALIGNED", "END_REALIGNED"]
        ].dropna()
        transcript = df.to_dict(orient="records")
        logger.info(f"Loaded {len(transcript)} transcript entries from {csv_file}.")
        return transcript
    except Exception as e:
        logger.error(f"Error loading CSV file {csv_file}: {e}")
        return []


def find_video_files(directory: str, pattern="*.mp4") -> Dict[str, str]:
    """
    Find all .mp4 files in the specified directory and return a dictionary
    mapping VIDEO_NAME to full file paths.
    """
    video_files = {}
    for f in glob(os.path.join(directory, pattern)):
        basename = os.path.splitext(os.path.basename(f))[0]
        video_files[basename] = f
    logger.info(f"Found {len(video_files)} video files in {directory}.")
    return video_files


def mediapipe_detection(image, model):
    return model.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))


def extract_keypoints(results):
    def landmarks_to_np(landmarks, indices):
        return (
            np.array(
                [[landmarks[i].x, landmarks[i].y, landmarks[i].z] for i in indices]
            )
            if landmarks
            else np.zeros((len(indices), 3))
        )

    pose = landmarks_to_np(
        getattr(results.pose_landmarks, "landmark", None), c.POSE_IDX
    )
    lh = landmarks_to_np(
        getattr(results.left_hand_landmarks, "landmark", None), c.HAND_IDX
    )
    rh = landmarks_to_np(
        getattr(results.right_hand_landmarks, "landmark", None), c.HAND_IDX
    )
    face = landmarks_to_np(
        getattr(results.face_landmarks, "landmark", None), c.FACE_IDX
    )

    return np.concatenate([pose.flatten(), face.flatten(), lh.flatten(), rh.flatten()])


def process_segment(segment_info: Dict, video_files: Dict[str, str]):
    """
    Process a single transcript entry:
    - Extract frames within the specified time interval.
    - Perform MediaPipe detection on each frame.
    - Save the landmarks to a .npy file in a directory named after SENTENCE_NAME.
    """
    video_name = segment_info["VIDEO_NAME"]
    sentence_name = segment_info["SENTENCE_NAME"]
    start_time = segment_info["START_REALIGNED"]
    end_time = segment_info["END_REALIGNED"]

    if video_name not in video_files:
        logger.error(f"Video {video_name} not found in available videos.")
        return

    video_path = video_files[video_name]
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Error opening video: {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    start_frame = int(start_time * fps)
    end_frame = int(end_time * fps)

    # Ensure frame indices are within bounds
    start_frame = max(0, min(start_frame, total_frames - 1))
    end_frame = max(0, min(end_frame, total_frames))

    frame_skip = 1  # Default: process every frame
    if c.LENGTH_BASED_MAX_FRAME and c.LENGTH_BASED_FRAME_SKIP:
        logger.error("Both LENGTH_BASED_MAX_FRAME and LENGTH_BASED_CONST are True.")
        return
    if c.LENGTH_BASED_MAX_FRAME:
        frame_skip = max(int(np.ceil((end_frame - start_frame) / c.MAX_FRAME)), 1)
    elif c.LENGTH_BASED_FRAME_SKIP:
        frame_skip = c.FRAME_SKIP

    all_landmarks = []

    with mp_holistic.Holistic(
        model_complexity=1,
        refine_face_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as holistic:
        current_frame = 0
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        while current_frame < (end_frame - start_frame):
            ret, frame = cap.read()
            if not ret:
                break
            if current_frame % frame_skip == 0:
                results = mediapipe_detection(frame, holistic)
                landmarks = extract_keypoints(results)
                all_landmarks.append(landmarks)
            current_frame += 1

    cap.release()

    data_array = np.array(all_landmarks)
    if data_array.size > 0 and np.any(data_array):
        os.makedirs(c.H2S_OUTPUT_DIR, exist_ok=True)
        output_file = os.path.join(c.H2S_OUTPUT_DIR, f"{sentence_name}.npy")
        np.save(output_file, data_array)
        logger.info(f"Saved landmarks to {output_file}")
    else:
        logger.info(f"No valid landmarks for segment {sentence_name}, not saving.")


def main():
    transcript_csv = c.H2S_CSV_FILE  # Updated to use H2S_CSV_FILE
    transcript = load_transcript(transcript_csv)
    if not transcript:
        logger.error("No transcript entries to process. Exiting.")
        return

    video_files = find_video_files(c.H2S_VIDEO_DIR)
    if not video_files:
        logger.error("No video files found. Exiting.")
        return

    # Use multiple processors
    with ProcessPoolExecutor(max_workers=c.MAX_WORKERS) as executor:
        futures = []
        for segment_info in transcript:
            futures.append(executor.submit(process_segment, segment_info, video_files))

        # Optionally, handle results or exceptions
        for future in futures:
            try:
                future.result()
            except Exception as e:
                logger.error(f"Error processing segment: {e}")


if __name__ == "__main__":
    main()
