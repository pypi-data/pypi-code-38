"""
SageMaker-specific exception handling.

"""
from sys import exit, stderr
from traceback import format_exc

from microcosm_sagemaker.constants import APP_HOOKS_GROUP, SagemakerPath


class DependencyCycleError(Exception):
    def __init__(self, component):
        super().__init__(f"Dependency cycle involving '{component}'.")


class AppHookNotFoundError(Exception):
    def __init__(self, hook_name):
        super().__init__(
            f"App hook '{hook_name}' undefined.  Please define '{hook_name}' "
            f"in {APP_HOOKS_GROUP}"
        )


def raise_sagemaker_exception(exception):
    traceback = format_exc()
    description = "Exception during training: " + str(exception) + "\n" + traceback + "\n"

    if not SagemakerPath.OUTPUT.exists():
        raise exception

    # Record the failure in a format that is saved along with the training run
    with open(SagemakerPath.OUTPUT / "failure", "w") as error_log:
        error_log.write(description)

    # Also display the status in the job logs
    stderr.write(description)

    # Mark training job as failed
    exit(255)
