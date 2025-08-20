# Backend Processing Module

This directory contains the backend processing modules for the PipelineApp, designed to run on cluster environments for video analysis and pose estimation.

## Overview

The backend consists of two main modules:
- **extract_pose.py**: DeepLabCut-based pose extraction from videos
- **preprocessing.py**: Video perspective transformation and format conversion

## Features

### Pose Extraction (`extract_pose.py`)
- DeepLabCut integration for pose estimation
- Batch processing support
- Configurable output formats (CSV/HDF5)
- Error logging and handling
- Command-line interface

### Video Preprocessing (`preprocessing.py`)
- Perspective transformation using corner detection
- Grayscale conversion
- Configurable output dimensions
- Progress tracking for long videos
- Error handling and validation

## Installation

### Prerequisites
- Python 3.8 or higher
- CUDA-compatible GPU (recommended for DeepLabCut)
- Sufficient storage space for video processing

### Install Dependencies
```bash
pip install -r requirements.txt
```

### For GPU Support (Optional)
If using CUDA-enabled GPUs make sure to install DeepLabCut with GPU support.

## Usage

### Pose Extraction

Extract pose data from a video using a pre-trained DeepLabCut model:

```bash
python extract_pose.py \
    --config_path /path/to/config.yaml \
    --video_path /path/to/video.mp4 \
    --out_folder /path/to/output \
    --batch_size 16 \
    --save_as_csv 1
```

#### Parameters:
- `--config_path`: Path to DeepLabCut config.yaml file
- `--video_path`: Path to input video file (required)
- `--video_type`: Video file extension (default: .mp4)
- `--out_folder`: Output directory (default: paths)
- `--shuffle`: Shuffle value for trained network (default: 1)
- `--batch_size`: Processing batch size (default: 16)
- `--save_as_csv`: Save as CSV (1) or HDF5 (0) (default: 1)

### Video Preprocessing

Transform video perspective and convert to grayscale:

```bash
python preprocessing.py \
    --video_path /path/to/video.mp4 \
    --corners /path/to/corners.npy \
    --folder_out /path/to/output \
    --boundary 100 \
    --output_width 1000 \
    --output_height 1000
```

#### Parameters:
- `--video_path`: Path to input video file (required)
- `--corners`: Path to .npy file with corner coordinates (required)
- `--folder_out`: Output directory (required)
- `--boundary`: Boundary padding in pixels (default: 100)
- `--output_width`: Output video width (default: 1000)
- `--output_height`: Output video height (default: 1000)

## Cluster Usage

### SLURM Example

Create a SLURM job script for cluster execution:

```bash
#!/bin/bash
#SBATCH --job-name=pose_extraction
#SBATCH --nodes=1
#SBATCH --gpus=1
#SBATCH --mem=32G
#SBATCH --time=04:00:00

module load python/3.8
source /path/to/venv/bin/activate

python extract_pose.py \
    --config_path $CONFIG_PATH \
    --video_path $VIDEO_PATH \
    --out_folder $OUTPUT_DIR \
    --batch_size 32
```

### PBS Example

```bash
#!/bin/bash
#PBS -N pose_extraction
#PBS -l nodes=1:ppn=8:gpus=1
#PBS -l mem=32gb
#PBS -l walltime=04:00:00

cd $PBS_O_WORKDIR
source /path/to/venv/bin/activate

python extract_pose.py \
    --config_path $CONFIG_PATH \
    --video_path $VIDEO_PATH \
    --out_folder $OUTPUT_DIR
```

## Error Handling

Both modules include comprehensive error handling:
- Input validation
- File existence checks
- Progress reporting
- Error logging to files
- Graceful failure handling

Error logs are written to:
- `error_log.txt` for pose extraction errors
- Console output for preprocessing errors

## Performance Considerations

### For Pose Extraction:
- Use GPU acceleration when available
- Adjust batch size based on available memory
- Consider video resolution and length
- Monitor GPU memory usage

### For Video Preprocessing:
- Large videos may require substantial disk space
- Processing time scales with video length
- Consider parallel processing for multiple videos

## Output Formats

### Pose Extraction Output:
- CSV files with coordinate data
- HDF5 files (if CSV disabled)
- Likelihood scores for each keypoint
- Metadata about the analysis

### Preprocessing Output:
- Grayscale MP4 videos
- Perspective-corrected frames
- Consistent dimensions across videos

## Troubleshooting

### Common Issues:

1. **DeepLabCut Import Error**:
   - Ensure DeepLabCut is properly installed
   - Check CUDA compatibility
   - Verify tensorflow version

2. **Video Codec Issues**:
   - Install additional codecs if needed
   - Try different video formats
   - Check OpenCV installation

3. **Memory Issues**:
   - Reduce batch size
   - Process shorter video segments
   - Monitor system resources

4. **File Path Issues**:
   - Use absolute paths when possible
   - Check file permissions
   - Verify file existence

## Contributing

When modifying the backend code:
1. Follow PEP 8 style guidelines
2. Include comprehensive docstrings
3. Add type hints where appropriate
4. Update error handling as needed
5. Test on cluster environment before deployment

## License

This backend module is part of the PipelineApp project. See the main project repository for license information.
