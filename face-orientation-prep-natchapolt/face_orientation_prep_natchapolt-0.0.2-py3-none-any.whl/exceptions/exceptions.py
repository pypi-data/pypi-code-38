class GivenImageNotValidError(Exception):
    """Raised when a given image object is corrupted or is empty"""
    pass

class FaceNotFoundOnImageError(Exception):
    """Raised when there is no face found on any possible orientation of the image"""
    pass