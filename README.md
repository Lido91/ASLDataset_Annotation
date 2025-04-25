# How2sign & Youtube-ASL Dataset Preprocess <!-- omit from toc -->

This repository follows the method from ["YouTube-ASL: A Large-Scale, Open-Domain American Sign Language-English Parallel Corpus" (Uthus et al., 2023)](https://arxiv.org/abs/2306.15162) which is designed to handle both **YouTube-ASL** and **How2Sign** datasets through **MediaPipe Holistic**. Our pipeline streamlines the workflow from video acquisition to landmark extraction, preparing the data for ASL translation tasks.

## Table of Contents<!-- omit from toc -->

- [Project Configuration](#project-configuration)
- [How to Use](#how-to-use)
  - [YouTube-ASL](#youtube-asl)
  - [How2Sign](#how2sign)
- [Dataset Introduction](#dataset-introduction)
  - [YouTube-ASL Dataset](#youtube-asl-dataset)
  - [How2Sign Dataset](#how2sign-dataset)

## Project Configuration

All project settings are managed through `conf.py`, offering a single configuration point for the preprocessing pipeline. Key elements include:

- `ID`: Text file containing YouTube video IDs to process
- `VIDEO_DIR`: Directory for downloaded videos
- `TRANSCRIPT_DIR`: Storage for JSON transcripts
- `OUTPUT_DIR`: Location for extracted features
- `CSV_FILE`: Path for processed segment data

- `YT_CONFIG`: YouTube download settings (video quality, format, rate limits)
- `LANGUAGE`: Supported language options for transcript retrieval
- `FRAME_SKIP`: Controls frame sampling rate for efficient processing
- `MAX_WORKERS`: Manages parallel processing to optimize performance

- `POSE_IDX`, `FACE_IDX`, `HAND_IDX`: Selected landmark indices for extracting relevant points for sign language analysis. Devault value is the index defined in YouTube-ASL Dataset's research paper.

## How to Use

### YouTube-ASL
1. Ensure the constants in `conf.py` are correct.
2. Run the following steps in order:
   - **Step 1: Data Acquisition** (`s1_data_downloader.py`)
     - **Necessary Constants:** `ID`, `VIDEO_DIR`, `TRANSCRIPT_DIR`, `YT_CONFIG`, `LANGUAGE`
     - The script skips already downloaded content and implements rate limiting to prevent API throttling.

   - **Step 2: Transcript Processing** (`s2_transcript_preprocess.py`)
     - **Necessary Constants:** `ID`, `TRANSCRIPT_DIR`, `CSV_FILE`
     - This step cleans text (converts Unicode characters, removes brackets), filters segments based on length and duration, and saves them with precise timestamps as tab-separated values.

   - **Step 3: Feature Extraction** (`s3_mediapipe_labelling.py`)
     - **Necessary Constants:** `CSV_FILE`, `VIDEO_DIR`, `OUTPUT_DIR`, `MAX_WORKERS`, `FRAME_SKIP`, `POSE_IDX`, `FACE_IDX`, `HAND_IDX`
- The script processes each video segment according to its timestamp, extracting only the most relevant body keypoints for sign language analysis. It uses parallel processing to handle multiple video efficiently. Results are saved as NumPy arrays.

### How2Sign
1. Download **Green Screen RGB videos** and **English Translation (manually re-aligned)** from the [How2Sign Website](https://how2sign.github.io/).
2. Place the directory and .csv file in the correct path or amend the path in `conf.py`.
3. Run **Step 3: Feature Extraction** (`s3_mediapipe_labelling.py`) only.

## Dataset Introduction

### YouTube-ASL Dataset
- **Video List**: [google-research/youtube_asl](https://github.com/google-research/google-research/blob/master/youtube_asl/README.md)
- **Paper**: ["YouTube-ASL: A Large-Scale, Open-Domain American Sign Language-English Parallel Corpus" (Uthus et al., 2023)](https://arxiv.org/abs/2306.15162)

If you use YouTube-ASL, please cite their associated paper:

```bibtex
@misc{uthus2023youtubeasl,
  author = {Uthus, David and Tanzer, Garrett and Georg, Manfred},
  title = {YouTube-ASL: A Large-Scale, Open-Domain American Sign Language-English Parallel Corpus},
  year = {2023},
  eprint = {2306.15162},
  archivePrefix = {arXiv},
  url = {https://arxiv.org/abs/2306.15162},
}
```

### How2Sign Dataset
- **Dataset**: [How2Sign Website](https://how2sign.github.io/)
- **Paper**: [How2Sign: A Large-scale Multimodal Dataset for Continuous American Sign Language](https://openaccess.thecvf.com/content/CVPR2021/html/Duarte_How2Sign_A_Large-Scale_Multimodal_Dataset_for_Continuous_American_Sign_Language_CVPR_2021_paper.html)

If you use How2Sign, please cite their associated paper:

```bibtex
@inproceedings{Duarte_CVPR2021,
    title={{How2Sign: A Large-scale Multimodal Dataset for Continuous American Sign Language}},
    author={Duarte, Amanda and Palaskar, Shruti and Ventura, Lucas and Ghadiyaram, Deepti and DeHaan, Kenneth and
                   Metze, Florian and Torres, Jordi and Giro-i-Nieto, Xavier},
    booktitle={Conference on Computer Vision and Pattern Recognition (CVPR)},
    year={2021}
}
```
