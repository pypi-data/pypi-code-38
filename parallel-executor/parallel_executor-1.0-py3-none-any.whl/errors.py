class ParallelExecutorError(Exception):
    """Base class for exceptions in the module."""
    pass

class AddTaskAfterStartError(Exception):
    """Exception which is raised if task is added to executor which already has been started or completed."""
    
