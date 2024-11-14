import os
import cv2
import mediapipe as mp
import numpy as np
import json
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor

# Initialize MediaPipe Holistic model components
mp_holistic = mp.solutions.holistic

def mediapipe_detection(image, model):
    # Convert the image color space from BGR to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # Process the image and detect the landmarks
    results = model.process(image_rgb)
    return results

def extract_keypoints(results):
    pose_indices = [11, 12, 13, 14, 23, 24]  # Shoulders and hips
    face_indices = [
        0, 4, 13, 14, 17, 33, 37, 39, 46, 52, 55, 61, 64, 81, 82, 93,
        133, 151, 152, 159, 172, 178, 181, 263, 269, 276, 282, 285, 291,
        294, 311, 323, 362, 386, 397, 468, 473
    ]  # 37 indices
    hand_indices = list(range(21))  # All 21 hand landmarks

    # Extract pose landmarks
    if results.pose_landmarks:
        pose_landmarks = results.pose_landmarks.landmark
        pose = np.array([[pose_landmarks[idx].x, pose_landmarks[idx].y, pose_landmarks[idx].z] for idx in pose_indices])
    else:
        pose = np.zeros((len(pose_indices), 3))

    # Extract left hand landmarks
    if results.left_hand_landmarks:
        lh_landmarks = results.left_hand_landmarks.landmark
        lh = np.array([[lh_landmarks[idx].x, lh_landmarks[idx].y, lh_landmarks[idx].z] for idx in hand_indices])
    else:
        lh = np.zeros((len(hand_indices), 3))

    # Extract right hand landmarks
    if results.right_hand_landmarks:
        rh_landmarks = results.right_hand_landmarks.landmark
        rh = np.array([[rh_landmarks[idx].x, rh_landmarks[idx].y, rh_landmarks[idx].z] for idx in hand_indices])
    else:
        rh = np.zeros((len(hand_indices), 3))

    # Extract selected facial landmarks (mouth, eyes, nose)
    if results.face_landmarks:
        face_landmarks = results.face_landmarks.landmark
        face = np.array([[face_landmarks[idx].x, face_landmarks[idx].y, face_landmarks[idx].z] for idx in face_indices])
    else:
        face = np.zeros((len(face_indices), 3))

    # Concatenate all landmarks
    keypoints = np.concatenate([pose.flatten(), face.flatten(), lh.flatten(), rh.flatten()])
    return keypoints


def process_video(video_file, output_directory, frame_rate=1):
    cap = cv2.VideoCapture(video_file)
    if not cap.isOpened():
        print(f"Error opening video file: {video_file}")
        return

    all_landmarks = []
    frame_index = 0

    # Initialize MediaPipe Holistic model
    with mp_holistic.Holistic(
        model_complexity=0,
        refine_face_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as holistic:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # Process every 3rd frame
            if frame_index % frame_rate == 0:
                # Perform MediaPipe detection
                results = mediapipe_detection(frame, holistic)
                # Extract keypoints for the frame
                keypoints = extract_keypoints(results)
                # Append keypoints to the list
                all_landmarks.append(keypoints)

            frame_index += 1  # Increment the frame index

    cap.release()

    # Convert all_landmarks to a NumPy array
    data_array = np.array(all_landmarks)  # Shape: (num_frames, 255)

    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)
    # Save the keypoints to a .npy file
    video_name = os.path.splitext(os.path.basename(video_file))[0]
    output_file = os.path.join(output_directory, f'{video_name}.npy')
    np.save(output_file, data_array)

    print(f'Landmarks for {video_file} successfully saved to {output_file}')


def process_videos_in_directory(input_directory, output_directory):
    # Process all video files in the directory
    video_extensions = ('.mp4', '.avi', '.mov', '.mkv')
    video_files = [
        os.path.join(input_directory, f)
        for f in os.listdir(input_directory)
        if f.lower().endswith(video_extensions)
    ]

    # Use ProcessPoolExecutor to process videos in parallel
    with ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(process_video, video_file, output_directory)
            for video_file in video_files
        ]
        # Wait for all futures to complete
        for future in futures:
            future.result()


def main():
    keypoints_directory = input("Enter the path to the main folder or a video file: ").strip()
    output_directory = input("Enter the path where the files will be saved: ").strip()

    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    if os.path.isfile(keypoints_directory):
        # If a single video file is provided
        if keypoints_directory.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            process_video(keypoints_directory, output_directory)
        else:
            print("Please provide a valid video file format (e.g., .mp4, .avi, .mov, .mkv)")
    elif os.path.isdir(keypoints_directory):
        # Process all video files in the directory
        process_videos_in_directory(keypoints_directory, output_directory)
    else:
        print("The provided path is neither a valid file nor a directory.")

if __name__ == '__main__':
    main()
