from enum import Enum
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_FOLDER = os.getenv("PROJECT_FOLDER", "//srv-fs.ad.nudz.cz/BV_data/TrackingPRC")


# TODO Switch to this version after debugging is completed
class FolderReleaseVersion(Enum):
    """Enumeration for folder paths used in the project."""
    VIDEOS = ".videos"
    VIDEOS_PREPROCESSED = ".videos_preprocessed"
    POINTS = ".points"
    TRACKING = ".tracking"
    IMAGES = "images"
    RESULTS = "results"

class Folder(Enum):
    """Enumeration for folder paths used in the project."""
    VIDEOS = "videos"
    VIDEOS_PREPROCESSED = "videos_preprocessed"
    POINTS = "points"
    TRACKING = "tracking"
    IMAGES = "images"
    RESULTS = "results"
