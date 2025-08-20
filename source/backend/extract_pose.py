"""
DeepLabCut pose extraction module for video analysis.

This module provides functionality to extract pose data from videos using
pre-trained DeepLabCut models on cluster environments.
"""

import traceback
from argparse import ArgumentParser
from pathlib import Path
from typing import Optional

import deeplabcut  # pyright: ignore[reportMissingImports]


def extract_pose(
    config_path: str,
    video_path: str,
    video_type: str = ".mp4",
    out_folder: str = "paths",
    shuffle: int = 1,
    batch_size: int = 16,
    save_as_csv: bool = True,
) -> None:
    """
    Extract pose data from a video using DeepLabCut.
    
    Args:
        config_path: Path to the DeepLabCut config.yaml file
        video_path: Path to the input video file
        video_type: Video file extension (default: .mp4)
        out_folder: Output directory for results (default: paths)
        shuffle: Shuffle value for the trained network (default: 1)
        batch_size: Batch size for processing (default: 16)
        save_as_csv: Whether to save results as CSV (default: True)
    
    Raises:
        Exception: If video analysis fails
    """
    try:
        deeplabcut.analyze_videos(
            config=config_path,
            videos=[video_path],
            videotype=video_type,
            shuffle=shuffle,
            save_as_csv=save_as_csv,
            destfolder=out_folder,
            batchsize=batch_size,
        )
        print(f"Successfully analyzed video: {video_path}")
        
    except Exception as e:
        error_msg = f"Error analyzing video {video_path}: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        
        # Log error to file
        error_log_path = Path("error_log.txt")
        with open(error_log_path, "a", encoding="utf-8") as f:
            f.write(f"\n{error_msg}\n")
        raise


def create_argument_parser() -> ArgumentParser:
    """Create and configure argument parser for command line interface."""
    parser = ArgumentParser(
        description="Extract pose data from videos using DeepLabCut",
        formatter_class=ArgumentParser.__dict__.get("ArgumentDefaultsHelpFormatter", ArgumentParser)
    )
    
    parser.add_argument(
        "--config_path",
        type=str,
        default="/home/vojtech.brejtr/projects/DLC_Basler/NPS-Basler-2025-02-19/config.yaml",
        help="Path to DeepLabCut config.yaml file"
    )
    parser.add_argument(
        "--video_path",
        type=str,
        required=True,
        help="Path to input video file"
    )
    parser.add_argument(
        "--video_type",
        type=str,
        default=".mp4",
        help="Video file extension"
    )
    parser.add_argument(
        "--out_folder",
        type=str,
        default="paths",
        help="Output directory for results"
    )
    parser.add_argument(
        "--shuffle",
        type=int,
        default=1,
        help="Shuffle value for trained network"
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=16,
        help="Batch size for processing"
    )
    parser.add_argument(
        "--save_as_csv",
        type=int,
        default=1,
        choices=[0, 1],
        help="Save results as CSV (1) or not (0)"
    )
    
    return parser


def main() -> None:
    """Main entry point for the pose extraction script."""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    Path(args.out_folder).mkdir(parents=True, exist_ok=True)
    
    extract_pose(
        config_path=args.config_path,
        video_path=args.video_path,
        video_type=args.video_type,
        out_folder=args.out_folder,
        shuffle=args.shuffle,
        batch_size=args.batch_size,
        save_as_csv=bool(args.save_as_csv),
    )


if __name__ == "__main__":
    main()