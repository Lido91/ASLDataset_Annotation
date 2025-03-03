# ASL Translation Data Preprocessing

This repository follows the methodology described in the YouTube-ASL Dataset paper and provides a comprehensive solution for preprocessing American Sign Language (ASL) datasets, specifically designed to handle both **How2Sign** and **YouTube-ASL** datasets. Our preprocessing pipeline streamlines the workflow from video acquisition to landmark extraction, making the data ready for ASL translation tasks.

## Project Configuration

All project settings are centrally managed through `conf.py`, providing a single point of configuration for the entire preprocessing pipeline. Key configuration elements include:

- `ID`: Text file containing YouTube video IDs to process
- `VIDEO_DIR`: Directory for downloaded videos
- `TRANSCRIPT_DIR`: Storage for JSON transcripts
- `OUTPUT_DIR`: Location for extracted features
- `CSV_FILE`: Path for processed segment data

- `YT_CONFIG`: YouTube download settings (video quality, format, rate limits)
- `LANGUAGE`: Supported language options for transcript retrieval
- `FRAME_SKIP`: Controls frame sampling rate for efficient processing
- `MAX_WORKERS`: Manages parallel processing to optimize performance

- `POSE_IDX`, `FACE_IDX`, `HAND_IDX`: Selected landmark indices for extracting the most relevant points for sign language analysis

This centralized approach allows easy adaptation to different hardware capabilities or dataset requirements without modifying the core processing code.
## How To Use?
- **YouTube-ASL**: make sure the constant is correct in conf.py. Then, operate step 1 to step 3. 
- **How2Sign**: download **Green Screen RGB videos** and **English Translation (manually re-aligned)** from How2Sign website. Put the directory and .csv file in the right path or amend the path in the conf.py. then, operate step 3 only.
  
### Step 1: Data Acquisition (s1_data_downloader.py)
**Necessary Constants:**`ID`, `VIDEO_DIR`, `TRANSCRIPT_DIR`, `YT_CONFIG`, `LANGUAGE`  
The script intelligently skips already downloaded content and implements rate limiting to prevent API throttling.



### Step 2: Transcript Processing (s2_transcript_preprocess.py)
**Necessary Constants:** `ID`, `TRANSCRIPT_DIR`, `CSV_FILE`  
This step cleans text (converts Unicode characters, removes brackets), filters segments based on length and duration, and saves them with precise timestamps as tab-separated values.



### Step 3: Feature Extraction (s3_mediapipe_labelling.py)
**Necessary Constants:** `CSV_FILE`, `VIDEO_DIR`, `OUTPUT_DIR`, `MAX_WORKERS`, `FRAME_SKIP`, `POSE_IDX`, `FACE_IDX`, `HAND_IDX`  
The script processes each video segment according to its timestamp, extracting only the most relevant body keypoints for sign language analysis. Results are saved as NumPy arrays.

## Dataset Introduction

### YouTube-ASL Dataset
Video List: [https://github.com/google-research/google-research/blob/master/youtube_asl/README.md](https://github.com/google-research/google-research/blob/master/youtube_asl/README.md)  
Paper: ["YouTube-ASL: A Large-Scale, Open-Domain American Sign Language-English Parallel Corpus" (Uthus et al., 2023)](https://arxiv.org/abs/2306.15162).

If you use YouTube-ASL, please cite their associated paper:

```
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
Dataset: [https://how2sign.github.io/](https://how2sign.github.io/)  
Paper: [How2Sign: A Large-scale Multimodal Dataset for Continuous American Sign Language](https://openaccess.thecvf.com/content/CVPR2021/html/Duarte_How2Sign_A_Large-Scale_Multimodal_Dataset_for_Continuous_American_Sign_Language_CVPR_2021_paper.html)

If you use How2Sign, please cite their associated paper:

```
@inproceedings{Duarte_CVPR2021,
    title={{How2Sign: A Large-scale Multimodal Dataset for Continuous American Sign Language}},
    author={Duarte, Amanda and Palaskar, Shruti and Ventura, Lucas and Ghadiyaram, Deepti and DeHaan, Kenneth and
                   Metze, Florian and Torres, Jordi and Giro-i-Nieto, Xavier},
    booktitle={Conference on Computer Vision and Pattern Recognition (CVPR)},
    year={2021}
}
```
