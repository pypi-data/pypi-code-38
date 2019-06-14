from enum import Enum

class ColTag(Enum):
    original = "original"
    modified = "modified"
    categorized = "categorized"
    mapping = "mapping"
    bad_indicator = "bad_indicator"
    engineered = "engineered"
    onehot = "onehot"