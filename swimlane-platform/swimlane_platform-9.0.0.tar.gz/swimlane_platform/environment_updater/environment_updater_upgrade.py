from typing import Dict, Union, List
from swimlane_platform.environment_updater.environment_updater_base import EnvironmentUpdaterBase
from swimlane_platform.lib import info_function_start_finish, ArgsConfigQuestions, names


class EnvironmentUpdaterUpgrade(EnvironmentUpdaterBase):

    @info_function_start_finish('Environment updater upgrade.')
    def run(self):
        # type: () -> None
        """
        Main method.
        """
        helper = self.docker_helper
        state = {}
        try:
            helper.containers_exists_validate(names.SW_WEB, names.SW_API, names.SW_TASKS, names.SW_MONGO)
            state = helper.containers_get_state(names.SW_WEB, names.SW_API, names.SW_TASKS)
            helper.containers_run(helper.container_stop, names.SW_WEB, names.SW_API, names.SW_TASKS)
            command = ['upgrade']
            self.get_admin_connection()
            self.run_image_command(command, {})
        finally:
            helper.container_restore_state(state)


def run(parent_config):
    # type: (Dict[str, Union[str, List[str]]]) -> None
    config = ArgsConfigQuestions(parent_config)
    upgrade = EnvironmentUpdaterUpgrade(config.to_arguments())
    upgrade.run()