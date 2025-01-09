# ASL Translation Data Preprocessing

This repository provides a comprehensive solution for preprocessing American Sign Language (ASL) datasets, specifically designed to handle both How2Sign and YouTube ASL datasets. Our preprocessing pipeline streamlines the workflow from video acquisition to landmark extraction, making the data ready for ASL translation tasks.

## Project Configuration

All project settings are centrally managed through `conf.py`, offering flexible configuration options for video processing, dataset management, and feature extraction. The configuration file controls several key aspects:

The system allows customization of video processing parameters, including frame skip rates and maximum frame limits, to optimize processing efficiency while maintaining data quality. It manages dataset paths and directories, ensuring organized data storage and retrieval. The configuration also specifies MediaPipe landmark indices for detailed capture of pose, face, and hand movements, essential for ASL translation. Additionally, it includes language preference settings for YouTube transcript collection, supporting various English language variants.

## YouTube ASL Dataset Processing

The processing of YouTube ASL dataset follows a systematic three-step approach, ensuring comprehensive data preparation:

### Step 1: Data Acquisition

This initial phase combines two parallel processes:

The video downloader (`s1_video_download.py`) efficiently retrieves YouTube videos using yt-dlp, implementing smart rate limiting and quality control measures. It includes features for parallel fragment downloads and automatically skips previously downloaded content to prevent redundant processing.

Simultaneously, the transcript collector (`s1_transcript_downloader.py`) obtains video transcripts through the YouTube Transcript API. This component handles multiple English language variants and saves the transcripts in a structured JSON format, while maintaining appropriate rate limits to ensure reliable data collection.

### Step 2: Transcript Enhancement

The transcript processor (`s2_transcript_preprocess.py`) refines the raw transcript data into a format suitable for ASL translation. It performs sophisticated text normalization, including Unicode handling and ASCII conversion, while preserving semantic meaning. The system segments videos into overlapping chunks with precise timing information, generating well-structured CSV files containing the processed segments.

### Step 3: Feature Extraction

The landmark extraction system (`s3_mediapipe_labelling.py`) utilizes the MediaPipe Holistic model to capture detailed movement data. It processes video segments to extract comprehensive pose, face, and hand landmarks, leveraging parallel processing capabilities for efficient computation. The extracted features are stored as numpy arrays for subsequent analysis and translation tasks.

## How2Sign Dataset Processing

For the How2Sign dataset, our system offers two specialized approaches for MediaPipe landmark extraction:

### Clip-Based Processing

The clip processor (`H2S_clip_mediapipe.py`) handles complete video clips in a single pass. It employs adaptive frame skipping to optimize processing speed while maintaining data quality. The system leverages parallel processing capabilities to handle multiple clips simultaneously, ensuring efficient resource utilization.

### Raw Video Processing

The raw video processor (`H2S_raw_mediapipe.py`) takes a more granular approach, working with precise realigned timestamps from a CSV file. This method extracts landmarks for specific video segments, maintaining temporal accuracy while utilizing parallel processing for optimal performance.

## Data Organization

The system organizes processed data into clearly defined formats:
- Video content is stored as MP4 files for optimal quality and compatibility
- Transcripts are maintained in JSON format for easy parsing and manipulation
- Segment information is organized in CSV files for straightforward analysis
- Extracted landmarks are preserved as NumPy arrays (.npy files) for efficient processing

## Technical Requirements

The system relies on several key Python libraries:
- OpenCV (cv2) for video processing
- MediaPipe for pose and gesture recognition
- NumPy for efficient numerical operations
- Pandas for data manipulation
- yt-dlp for video downloading
- youtube-transcript-api for transcript retrieval

This preprocessing pipeline creates a robust foundation for ASL translation tasks, ensuring high-quality data preparation while maintaining processing efficiency.
