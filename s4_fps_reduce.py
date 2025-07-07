import os
import numpy as np
import cv2
from glob import glob
from typing import Dict, List, Tuple
import logging
from concurrent.futures import ProcessPoolExecutor

import conf as c

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_video_fps(video_path: str) -> float:
    """
    Get the FPS of a video file.
    
    Args:
        video_path (str): Path to the video file
        
    Returns:
        float: FPS of the video
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Error opening video: {video_path}")
        return 0.0
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    return fps


def get_npy_filenames(directory: str, pattern="*.npy") -> List[str]:
    """
    Retrieves npy filenames from specified directory without extensions.
    
    Args:
        directory (str): Directory path to search for npy files
        pattern (str): File pattern to match (default: "*.npy")
        
    Returns:
        List[str]: List of filenames without extensions
    """
    return [
        os.path.splitext(os.path.basename(f))[0]
        for f in glob(os.path.join(directory, pattern))
    ]


def calculate_frame_skip(original_fps: float, target_fps: float) -> int:
    """
    Calculate the frame skip interval to achieve target FPS.
    
    Args:
        original_fps (float): Original FPS of the data
        target_fps (float): Target FPS to achieve
        
    Returns:
        int: Frame skip interval (1 means no skipping)
    """
    if target_fps >= original_fps:
        return 1
    return max(1, int(original_fps / target_fps))


def reduce_fps_npy(npy_file: str, video_path: str, target_fps: float, output_dir: str):
    """
    Reduce FPS of landmark data stored in npy file.
    
    Args:
        npy_file (str): Path to input npy file
        video_path (str): video_path to get original FPS
        target_fps (float): Target FPS to achieve
        output_dir (str): Directory to save reduced FPS files
    """
    try:
        # Load the npy file
        landmark_data = np.load(npy_file)
        
        # Get original video FPS
        original_fps = get_video_fps(video_path)
        
        if original_fps == 0:
            logger.error(f"Could not get FPS for video: {video_path}")
            return
        if c.FRAME_SKIP != 1:
            logger.warning(f"Applying frame skip factor: {c.FRAME_SKIP} to original FPS: {original_fps}")
            original_fps = original_fps / c.FRAME_SKIP
        
        # Calculate frame skip
        frame_skip = calculate_frame_skip(original_fps, target_fps)
        
        # Apply frame skip to reduce data
        reduced_data = landmark_data[::frame_skip]
        
        # Create output filename
        filename = os.path.basename(npy_file)
        output_file = os.path.join(output_dir, f"{filename}")
        
        # Save reduced data
        os.makedirs(output_dir, exist_ok=True)
        np.save(output_file, reduced_data)

        logger.info(f"File: {filename} from {len(landmark_data)} to {len(reduced_data)}")
        logger.info(f"Saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"Error processing {npy_file}: {e}")


def process_fps_reduction(npy_file: str, target_fps: float, output_dir: str):
    """
    Process a single npy file for FPS reduction.
    
    Args:
        npy_file (str): Path to the npy file
        target_fps (float): Target FPS to achieve
        output_dir (str): Output directory for reduced files
    """
    # Extract video ID from filename (format: video_id-segment_id.npy)
    filename = os.path.basename(npy_file)
    video_id = filename.split("-")[0]
    video_path = os.path.join(c.VIDEO_DIR, f"{video_id}.mp4")
    
    reduce_fps_npy(npy_file, video_path, target_fps, output_dir)


def main():
    """
    Main function to orchestrate FPS reduction of npy files.
    """
    # Configuration
    INPUT_DIR = c.NPY_DIR  # Use existing npy files as input
    TARGET_FPS = c.TARGET_FPS  # Target FPS for reduction
    OUTPUT_DIR = f"{c.ROOT}/dataset/npy_fps{TARGET_FPS:.0f}/"
    
    # Get all npy files
    npy_files = glob(os.path.join(INPUT_DIR, "*.npy"))
    
    if not npy_files:
        logger.error(f"No npy files found in {INPUT_DIR}")
        return
    
    logger.info(f"Found {len(npy_files)} npy files to process")
    logger.info(f"Target FPS: {TARGET_FPS}")
    logger.info(f"Output directory: {OUTPUT_DIR}")
    
    # Process files in parallel
    with ProcessPoolExecutor(max_workers=c.MAX_WORKERS) as executor:
        for npy_file in npy_files:
            executor.submit(process_fps_reduction, npy_file, TARGET_FPS, OUTPUT_DIR)


if __name__ == "__main__":
    main()