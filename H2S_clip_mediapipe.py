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


def read_timestamp_data(csv_file: str) -> Dict[str, List[float]]:
    """
    Reads and processes timestamp data from a CSV file.

    Args:
        csv_file (str): Path to the CSV file containing timestamp information

    Returns:
        Dict[str, List[float]]: Dictionary mapping segment names to [start, end] timestamps
    """
    try:
        df = pd.read_csv(csv_file, delimiter=",", on_bad_lines="skip")[
            ["SENTENCE_NAME", "START", "END"]
        ].dropna()
        return (
            df.set_index("SENTENCE_NAME")[["START", "END"]]
            .apply(lambda row: [row["START"], row["END"]], axis=1)
            .to_dict()
        )
    except Exception as e:
        logger.error(f"Error loading CSV file {csv_file}: {e}")
        return {}


def get_video_filenames(directory: str, pattern="*.mp4") -> List[str]:
    """
    Retrieves video filenames from specified directory without extensions.

    Args:
        directory (str): Directory path to search for video files
        pattern (str): File pattern to match (default: "*.mp4")

    Returns:
        List[str]: List of filenames without extensions
    """
    return [
        os.path.splitext(os.path.basename(f))[0]
        for f in glob(os.path.join(directory, pattern))
    ]


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


def process_complete_video(video_path: str, output_file: str):
    """
    Processes an entire video to extract holistic keypoints and saves them.

    Args:
        video_path (str): Path to input video file
        output_file (str): Path to save extracted landmarks
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Error opening video: {video_path}")
        return

    # Get video properties and determine frame skip rate
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Calculate frame skip based on configuration
    if c.LENGTH_BASED_MAX_FRAME and c.LENGTH_BASED_FRAME_SKIP:
        logger.error("Both LENGTH_BASED_MAX_FRAME and LENGTH_BASED_CONST are True.")
        return

    frame_skip = (
        np.ceil(total_frames / c.MAX_FRAME)
        if c.LENGTH_BASED_MAX_FRAME
        else c.FRAME_SKIP if c.LENGTH_BASED_FRAME_SKIP else 1
    )

    landmark_sequences = []
    with mp_holistic.Holistic(
        model_complexity=1,
        refine_face_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as holistic:
        current_frame = 0
        while current_frame < total_frames:
            ret, frame = cap.read()
            if not ret:
                break
            if current_frame % frame_skip == 0:
                results = process_mediapipe_detection(frame, holistic)
                landmark_sequences.append(extract_landmark_coordinates(results))
            current_frame += 1

    cap.release()

    # Save landmarks if valid data exists
    landmark_array = np.array(landmark_sequences)
    if landmark_array.size > 0 and np.any(landmark_array):
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        np.save(output_file, landmark_array)
        logger.info(f"Saved landmarks to {output_file}")
    else:
        logger.info(f"No valid landmarks for video {video_path}, not saving.")


def main():
    """
    Main function to orchestrate video processing and landmark extraction.
    Handles file management and parallel processing of complete videos.
    """
    video_files = get_video_filenames(c.H2S_VIDEO_DIR)
    processed_files = get_video_filenames(c.H2S_OUTPUT_DIR, pattern="*.npy")

    processing_tasks = []
    for video_name in video_files:
        video_path = os.path.join(c.H2S_VIDEO_DIR, f"{video_name}.mp4")
        output_path = os.path.join(c.H2S_OUTPUT_DIR, f"{video_name}.npy")
        if video_name not in processed_files:
            processing_tasks.append((video_path, output_path))
        else:
            logger.info(f"Skipping existing file: {output_path}")

    # Process videos in parallel
    with ProcessPoolExecutor(max_workers=c.MAX_WORKERS) as executor:
        for video_path, output_path in processing_tasks:
            executor.submit(process_complete_video, video_path, output_path)


if __name__ == "__main__":
    main()
