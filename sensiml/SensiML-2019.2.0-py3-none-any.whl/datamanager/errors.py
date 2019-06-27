class DataManagerError(Exception):
    pass


class AsyncObjectError(DataManagerError):
    pass


class AsyncObjectNotReadyError(AsyncObjectError):
    pass


class CaptureNotReadyError(AsyncObjectNotReadyError):
    pass


class AsyncObjectFailureError(AsyncObjectError):
    """When object processing/upload fails"""
    pass


class CaptureUploadFailureError(AsyncObjectFailureError):
    pass

# Renamed to event


class EventNotReadyError(CaptureNotReadyError):
    """Alias for CaptureNotReadyError since Captures
        are called Events in some locations."""
    pass


class EventUploadFailureError(CaptureUploadFailureError):
    pass
