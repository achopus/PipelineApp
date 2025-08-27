"""
Video preprocessing module for perspective transformation and format conversion.

This module provides functionality to transform video perspectives using corner
detection and convert videos to grayscale format for further analysis.
"""

import os
from argparse import ArgumentParser
from pathlib import Path
from typing import Tuple

import cv2
import numpy as np


class VideoPreprocessor:
    """Video preprocessing utility for perspective transformation and format conversion."""
    
    def __init__(self, boundary: int = 100, output_size: Tuple[int, int] = (1000, 1000)):
        """
        Initialize the video preprocessor.
        
        Args:
            boundary: Boundary padding in pixels (default: 100)
            output_size: Output video dimensions as (width, height) (default: 1000x1000)
        """
        self.boundary = boundary
        self.output_width, self.output_height = output_size
        
        # Define target corners for perspective transformation
        self.target_corners = np.array([
            [boundary, boundary],  # Top-left
            [self.output_width + boundary, boundary],  # Top-right
            [self.output_width + boundary, self.output_height + boundary],  # Bottom-right
            [boundary, self.output_height + boundary]  # Bottom-left
        ], dtype=np.float32)
    
    def transform_video(self, video_path: str, corners_path: str, output_folder: str) -> str:
        """
        Transform video perspective and convert to grayscale.
        
        Args:
            video_path: Path to input video file
            corners_path: Path to .npy file containing corner coordinates
            output_folder: Directory to save the transformed video
        
        Returns:
            Path to the output video file
            
        Raises:
            FileNotFoundError: If input files don't exist
            ValueError: If video cannot be opened or corners are invalid
        """
        # Validate input files
        if not Path(video_path).exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        if not Path(corners_path).exists():
            raise FileNotFoundError(f"Corners file not found: {corners_path}")
        
        # Create output directory
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        
        # Load corner coordinates
        try:
            source_corners = np.load(corners_path).astype(np.float32)
        except Exception as e:
            raise ValueError(f"Failed to load corners from {corners_path}: {e}")
        
        if source_corners.shape != (4, 2):
            raise ValueError(f"Expected 4x2 corner array, got {source_corners.shape}")
        
        # Open video capture
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        try:
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Calculate transformation matrix
            transformation_matrix = cv2.getPerspectiveTransform(source_corners, self.target_corners)
            
            # Set up output video
            output_width = self.output_width + 2 * self.boundary
            output_height = self.output_height + 2 * self.boundary
            output_size = (output_width, output_height)
            
            # Create output path
            output_filename = Path(video_path).name
            output_path = os.path.join(output_folder, output_filename)
            
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v') # pyright: ignore[reportAttributeAccessIssue]
            writer = cv2.VideoWriter(output_path, fourcc, fps, output_size, isColor=False)
            
            if not writer.isOpened():
                raise ValueError(f"Cannot create video writer for: {output_path}")
            
            # Process frames
            frame_number = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Apply perspective transformation
                transformed_frame = cv2.warpPerspective(frame, transformation_matrix, output_size)
                
                # Convert to grayscale
                if len(transformed_frame.shape) == 3:
                    grayscale_frame = cv2.cvtColor(transformed_frame, cv2.COLOR_BGR2GRAY)
                else:
                    grayscale_frame = transformed_frame
                
                writer.write(grayscale_frame)
                frame_number += 1
                
            return output_path
            
        finally:
            cap.release()
            writer.release()


def create_argument_parser() -> ArgumentParser:
    """Create and configure argument parser for command line interface."""
    parser = ArgumentParser(
        description="Transform video perspective and convert to grayscale"
    )
    
    parser.add_argument(
        "--video_path",
        type=str,
        required=True,
        help="Path to input video file"
    )
    parser.add_argument(
        "--corners",
        type=str,
        required=True,
        help="Path to .npy file containing corner coordinates"
    )
    parser.add_argument(
        "--folder_out",
        type=str,
        required=True,
        help="Output directory for transformed video"
    )
    parser.add_argument(
        "--boundary",
        type=int,
        default=100,
        help="Boundary padding in pixels"
    )
    parser.add_argument(
        "--output_width",
        type=int,
        default=1000,
        help="Output video width in pixels"
    )
    parser.add_argument(
        "--output_height",
        type=int,
        default=1000,
        help="Output video height in pixels"
    )
    
    return parser


def main() -> None:
    """Main entry point for the video preprocessing script."""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Initialize preprocessor
    preprocessor = VideoPreprocessor(
        boundary=args.boundary,
        output_size=(args.output_width, args.output_height)
    )
    
    # Transform video
    try:
        output_path = preprocessor.transform_video(
            video_path=args.video_path,
            corners_path=args.corners,
            output_folder=args.folder_out
        )

    except Exception as e:
        with open("error_log.txt", "a") as log_file:
            log_file.write(f"Error occurred in main: {e}\n")
        raise


if __name__ == "__main__":
    main()

