from enum import Enum

class Status(Enum):
    ERROR = -1
    LOADED = 1
    READY_PREPROCESS = 2
    PREPROCESSING_IN_PROGRESS = 3
    READY_TRACKING = 4
    TRACKED = 5
    RESULTS_DONE = 6
