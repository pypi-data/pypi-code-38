#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
__all__ = ["CameraNotFound", "FrameCaptureFailed", "FrameRejected"]

class CameraNotFound(Exception):
    """Exception for a camera startup failure.
    """

class FrameCaptureFailed(Exception):
    """Exception for a frame capture failure
    """

class FrameRejected(Exception):
    """Exception for rejected frames.
    """
    pass
