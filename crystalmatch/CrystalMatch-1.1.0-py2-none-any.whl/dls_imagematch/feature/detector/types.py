class DetectorType:
    def __init__(self):
        pass

    ORB = "ORB"
    SIFT = "SIFT"
    SURF = "SURF"
    BRISK = "BRISK"
    FAST = "FAST"
    STAR = "STAR"
    MSER = "MSER"
    GFTT = "GFTT"
    HARRIS = "HARRIS"
    DENSE = "Dense"
    BLOB = "SimpleBlob"
    
    LIST_ALL = [ORB, SIFT, SURF, BRISK, MSER, FAST, STAR, GFTT, HARRIS, DENSE, BLOB]
    LIST_FREE = [ORB, BRISK, FAST, STAR, MSER, GFTT, HARRIS, DENSE, BLOB]
    LIST_NON_FREE = [SIFT, SURF]

    @staticmethod
    def is_non_free(detector):
        return detector in DetectorType.LIST_NON_FREE


class ExtractorType:
    """ Note: SIFT descriptors for a keypoint are an array of 128 integers; SURF descriptors are an
    array of 64 floats (in range -1 to 1); BRISK uses 64 integers, ORB and BRIEF are arrays of 32 ints
    (in range 0 to 255). """
    def __init__(self):
        pass

    # Extractor Types
    ORB = "ORB"
    SURF = "SURF"
    SIFT = "SIFT"
    BRISK = "BRISK"
    BRIEF = "BRIEF"

    LIST_ALL = [ORB, SURF, SIFT, BRIEF, BRISK]

    @staticmethod
    def distance_factor(factor_type):
        """ Each extractor type has a different keypoint representation and so a different metric is used
        for calculating the match keypoint distance in each case. Consequently, the values of keypoint
        distance from two different extractor methods are not directly comparable (e.g. SURF produces
        distances in the range 0-1, whereas SIFT are in the range 100-1000). These distance factors
        bring the distances from each extractor method into roughly the same range (1-100). """
        if factor_type == ExtractorType.ORB:
            return 1
        elif factor_type == ExtractorType.SURF:
            return 100
        elif factor_type == ExtractorType.SIFT:
            return 0.1
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
