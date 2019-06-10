import os

from typing import Callable


class _AmlEnvironmentVariables:
    _tracked_env_vars = ['AZUREML_RUN_TOKEN', 'AZUREML_ARM_SUBSCRIPTION', 'AZUREML_ARM_RESOURCEGROUP',
                         'AZUREML_ARM_WORKSPACE_NAME', 'AZUREML_SERVICE_ENDPOINT', 'AZUREML_ARM_PROJECT_NAME',
                         'AZUREML_RUN_ID']

    def __init__(self):
        self._existing_values = {}
        for var in _AmlEnvironmentVariables._tracked_env_vars:
            self._existing_values[var] = os.environ.get(var)

    def get_changed(self) -> dict:
        changed = {}
        for var in _AmlEnvironmentVariables._tracked_env_vars:
            existing = self._existing_values[var]
            new = os.environ.get(var)
            if existing != new:
                self._existing_values[var] = new
                changed[var] = new
        return changed


def update_aml_env_vars(engine_api_func: Callable[[], 'EngineAPI']):
    def decorator(send_message_func: Callable[[str, object], object]):
        from functools import wraps

        aml_env_vars = _AmlEnvironmentVariables()

        @wraps(send_message_func)
        def wrapper(op_code: str, message: object) -> object:
            changed = aml_env_vars.get_changed()
            if len(changed) > 0:
                engine_api_func().update_environment_variable(changed)
            return send_message_func(op_code, message)

        return wrapper
    return decorator
