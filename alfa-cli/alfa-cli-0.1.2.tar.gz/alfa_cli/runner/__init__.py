import os
import json

from alfa_sdk.common.stores import ConfigStore
from alfa_sdk.common.helpers import AlfaConfigHelper
from alfa_sdk.common.exceptions import AlfaConfigError
from alfa_cli.common.exceptions import RuntimeError
from alfa_cli.runner.python import PythonRunner


class LocalRunner:
    def __init__(self, obj):
        self.config = AlfaConfigHelper.load(os.path.join(".", "alfa.yml"), is_package=False)
        self.invoke_config = self.get_invoke_config()
        self.runner = self.create_runner()

        self.set_context(obj)

    #

    def set_context(self, obj):
        user = obj["client"].user

        user_id = user["userId"]
        team_id = user["teamId"]
        algorithm_id = self.config["id"]
        algorithm_environment = self.config["environment"]
        alfa_environment = ConfigStore.get_value("alfa_env", group="alfa")
        algorithm_environment_id = f"{team_id}:{algorithm_id}:{algorithm_environment}"

        context = {
            "userId": user_id,
            "teamId": team_id,
            "alfaEnvironment": alfa_environment,
            "algorithmEnvironmentId": algorithm_environment_id,
            "algorithmRunId": -1,
        }

        os.environ["ALFA_CONTEXT"] = json.dumps(context)
        return context

    def create_runner(self):
        runtime = self.get_runtime()

        if "python" in runtime:
            return PythonRunner(self.invoke_config)
        else:
            raise RuntimeError(message=f"Runtime '{runtime}' not supported")

    #

    def get_invoke_config(self):
        ERROR_MESSAGE = "invoke function not defined"

        functions = self.config.get("functions")
        if not functions:
            raise AlfaConfigError(message='Invalid configuration', error=ERROR_MESSAGE)

        invoke_functions = [func for func in functions if "invoke" in func.keys()]
        if len(invoke_functions) == 0:
            raise AlfaConfigError(message='Invalid configuration', error=ERROR_MESSAGE)

        invoke_function = invoke_functions[0]
        return invoke_function["invoke"]

    def get_runtime(self):
        ERROR_MESSAGE = "runtime not defined"

        provider = self.invoke_config.get("provider")
        if not provider:
            raise AlfaConfigError(message='Invalid configuration', error=ERROR_MESSAGE)

        runtime = provider.get("runtime")
        if not runtime:
            raise AlfaConfigError(message='Invalid configuration', error=ERROR_MESSAGE)

        return runtime

    #

    def run(self, problem):
        return self.runner.run(problem)
