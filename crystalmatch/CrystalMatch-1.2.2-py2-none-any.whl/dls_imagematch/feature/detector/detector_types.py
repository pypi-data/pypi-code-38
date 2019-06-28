class DetectorType:
    def __init__(self):
        pass

    ORB = "ORB"
    BRISK = "BRISK"
    FAST = "FAST"
    STAR = "STAR"
    MSER = "MSER"
    GFTT = "GFTT"
    HARRIS = "HARRIS"
    BLOB = "SimpleBlob"

    LIST_ALL = [ORB, BRISK, FAST, STAR, MSER, BLOB, GFTT, HARRIS] #GFTT, HARRIS,
    LIST_WITHOUT_EXTRACTORS = [FAST, STAR, MSER, BLOB, GFTT, HARRIS] #GFFT and HARRIS not working errror -209

class ExtractorType:
    def __init__(self):
        pass

    BRIEF = "BRIEF"
    ORB = "ORB"
    BRISK = "BRISK"

    LIST_ALL = [BRIEF, ORB, BRISK]

    @staticmethod
    def distance_factor(factor_type):
        """ Each extractor type has a different keypoint representation and so a different metric is used
        for calculating the match keypoint distance in each case. """
        if factor_type == ExtractorType.ORB:
            return 1
        elif factor_type == ExtractorType.BRISK:
            return 0.1
        elif factor_type == ExtractorType.BRIEF:
            return 1


class AdaptationType:
    def __init__(self):
        pass

    NONE = ""
    GRID = "Grid"
    PYRAMID = "Pyramid"

    LIST_ALL = [NONE, GRID, PYRAMID]
