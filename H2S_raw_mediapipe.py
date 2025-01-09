import os
import cv2
import mediapipe as mp
import numpy as np
import logging
from glob import glob
from typing import List, Dict
from concurrent.futures import ProcessPoolExecutor
import pandas as pd

import conf as c  # Keeping original conf import name

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

mp_holistic = mp.solutions.holistic


def read_alignment_data(csv_file: str) -> List[Dict]:
    """
    Reads and processes time-aligned transcript data from a CSV file.

    Args:
        csv_file (str): Path to tab-separated CSV file containing video alignments

    Returns:
        List[Dict]: List of dictionaries containing video metadata including
                   VIDEO_NAME, SENTENCE_NAME, START_REALIGNED, and END_REALIGNED
    """
    try:
        df = pd.read_csv(csv_file, delimiter="\t", on_bad_lines="skip")[
            ["VIDEO_NAME", "SENTENCE_NAME", "START_REALIGNED", "END_REALIGNED"]
        ].dropna()
        alignment_data = df.to_dict(orient="records")
        logger.info(f"Loaded {len(alignment_data)} transcript entries from {csv_file}.")
        return alignment_data
    except Exception as e:
        logger.error(f"Error loading CSV file {csv_file}: {e}")
        return []


def map_video_paths(directory: str, pattern="*.mp4") -> Dict[str, str]:
    """
    Creates a mapping of video names to their full file paths.

    Args:
        directory (str): Directory containing video files
        pattern (str): File pattern to match (default: "*.mp4")

    Returns:
        Dict[str, str]: Dictionary mapping video names to their full file paths
    """
    video_path_map = {}
    for filepath in glob(os.path.join(directory, pattern)):
        video_name = os.path.splitext(os.path.basename(filepath))[0]
        video_path_map[video_name] = filepath
    logger.info(f"Found {len(video_path_map)} video files in {directory}.")
    return video_path_map


def process_mediapipe_detection(image, model):
    """
    Processes an image through MediaPipe detection model.

    Args:
        image: Input image in BGR format
        model: MediaPipe model instance

    Returns:
        MediaPipe detection results
    """
    return model.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))


def extract_landmark_coordinates(results):
    """
    Extracts landmark coordinates from MediaPipe detection results.

    Args:
        results: MediaPipe detection results

    Returns:
        np.ndarray: Concatenated array of pose, face, and hand landmarks
    """

    def convert_landmarks_to_array(landmarks, indices):
        return (
            np.array(
                [[landmarks[i].x, landmarks[i].y, landmarks[i].z] for i in indices]
            )
            if landmarks
            else np.zeros((len(indices), 3))
        )

    # Extract landmarks for different body parts
    pose_landmarks = convert_landmarks_to_array(
        getattr(results.pose_landmarks, "landmark", None), c.POSE_IDX
    )
    left_hand = convert_landmarks_to_array(
        getattr(results.left_hand_landmarks, "landmark", None), c.HAND_IDX
    )
    right_hand = convert_landmarks_to_array(
        getattr(results.right_hand_landmarks, "landmark", None), c.HAND_IDX
    )
    face_landmarks = convert_landmarks_to_array(
        getattr(results.face_landmarks, "landmark", None), c.FACE_IDX
    )

    return np.concatenate(
        [
            pose_landmarks.flatten(),
            face_landmarks.flatten(),
            left_hand.flatten(),
            right_hand.flatten(),
        ]
    )


def process_video_segment(segment_info: Dict, video_paths: Dict[str, str]):
    """
    Processes a video segment to extract and save MediaPipe landmarks.

    Args:
        segment_info (Dict): Dictionary containing segment information including
                           video name, sentence name, and time alignments
        video_paths (Dict[str, str]): Mapping of video names to file paths

    The function extracts frames within the specified time interval,
    performs MediaPipe detection, and saves landmarks to a numpy file.
    """
    video_name = segment_info["VIDEO_NAME"]
    sentence_name = segment_info["SENTENCE_NAME"]
    start_time = segment_info["START_REALIGNED"]
    end_time = segment_info["END_REALIGNED"]

    if video_name not in video_paths:
        logger.error(f"Video {video_name} not found in available videos.")
        return

    # Initialize video capture
    video_path = video_paths[video_name]
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Error opening video: {video_path}")
        return

    # Calculate frame indices
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    start_frame = max(0, min(int(start_time * fps), total_frames - 1))
    end_frame = max(0, min(int(end_time * fps), total_frames))

    # Determine frame skip rate based on configuration
    frame_skip = 1
    if c.LENGTH_BASED_MAX_FRAME and c.LENGTH_BASED_FRAME_SKIP:
        logger.error("Both LENGTH_BASED_MAX_FRAME and LENGTH_BASED_CONST are True.")
        return
    if c.LENGTH_BASED_MAX_FRAME:
        frame_skip = max(int(np.ceil((end_frame - start_frame) / c.MAX_FRAME)), 1)
    elif c.LENGTH_BASED_FRAME_SKIP:
        frame_skip = c.FRAME_SKIP

    landmark_sequences = []
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
                results = process_mediapipe_detection(frame, holistic)
                landmarks = extract_landmark_coordinates(results)
                landmark_sequences.append(landmarks)
            current_frame += 1

    cap.release()

    # Save landmarks if valid data exists
    landmark_array = np.array(landmark_sequences)
    if landmark_array.size > 0 and np.any(landmark_array):
        os.makedirs(c.H2S_OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(c.H2S_OUTPUT_DIR, f"{sentence_name}.npy")
        np.save(output_path, landmark_array)
        logger.info(f"Saved landmarks to {output_path}")
    else:
        logger.info(f"No valid landmarks for segment {sentence_name}, not saving.")


def main():
    """
    Main function to orchestrate video segment processing and landmark extraction.
    Handles loading of alignment data, video path mapping, and parallel processing.
    """
    alignment_data = read_alignment_data(c.H2S_CSV_FILE)
    if not alignment_data:
        logger.error("No alignment entries to process. Exiting.")
        return

    video_path_map = map_video_paths(c.H2S_VIDEO_DIR)
    if not video_path_map:
        logger.error("No video files found. Exiting.")
        return

    # Process video segments in parallel
    with ProcessPoolExecutor(max_workers=c.MAX_WORKERS) as executor:
        futures = []
        for segment_info in alignment_data:
            futures.append(
                executor.submit(process_video_segment, segment_info, video_path_map)
            )

        # Handle processing results and exceptions
        for future in futures:
            try:
                future.result()
            except Exception as e:
                logger.error(f"Error processing segment: {e}")


if __name__ == "__main__":
    main()
