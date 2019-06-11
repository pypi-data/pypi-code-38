"""Errors raise by Fussy explicitly
"""
class FussyError( Exception ):
    """Base class on which all other Fussy specific errors are based"""
    EXIT_CODE = 2

class SystemSetupError( RuntimeError, FussyError ):
    """System configuration appears incorrect (missing required packages, etc)
    
    Recovery will likely require system-level intervention
    """
    EXIT_CODE = 40

class RevertedFailure( FussyError ):
    """Error when failure occurred, but were able to revert to previous/failsafe
    
    No recovery is required, the previous version of the firmware was restored
    """
    EXIT_CODE = 3
class UnrecoverableError( FussyError ):
    """Error raised when there's just no way to recover"""
    EXIT_CODE = 4

class SignatureFailure( FussyError ):
    """Signature was incorrect, or could not be verified
    
    No recovery is required, the archive was rejected before install
    """
    EXIT_CODE = 20
class ArchiveFailure( FussyError ):
    """Archive appears incorrectly structured
    
    No recovery is required, the archive was rejected before install
    """
    EXIT_CODE = 21
