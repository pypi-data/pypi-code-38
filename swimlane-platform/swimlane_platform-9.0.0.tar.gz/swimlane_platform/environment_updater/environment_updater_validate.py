from swimlane_platform.environment_updater.environment_updater_base import EnvironmentUpdaterBase
from swimlane_platform.lib import names, ArgsConfigQuestions, info_function_start_finish, \
    VersionValidator, ContainingDirectoryExistsValidator


class EnvironmentUpdaterValidate(EnvironmentUpdaterBase):

    @info_function_start_finish('Swimlane validate.')
    def run(self):
        # type: () -> None
        """
        Main method.
        """
        self.docker_helper.containers_exists_validate(names.SW_API, names.SW_MONGO)
        local, remote = self.parse_file_location(self.args.report_file)
        command = ['validate', '-f', remote]
        # Not pulled up to parent, because in the future EU needs to be fixed.
        self.get_admin_connection()
        self.run_image_command(command, {local: {'bind': self.REPORT_FOLDER, 'mode': 'rw'}})


def run(parent_config):
    # type: (ArgsConfigQuestions) -> None
    questions = [
        {
            'type': 'input',
            'name': 'report_file',
            'message': 'Specify the path to the output validation report file.',
            'validate': ContainingDirectoryExistsValidator
        },
        {
            'type': 'input',
            'name': 'version',
            'message': 'Specify the version to validate.',
            'validate': VersionValidator
        }
    ]
    config = ArgsConfigQuestions(parent_config)
    config.collect(questions)
    validate = EnvironmentUpdaterValidate(config.to_arguments())
    validate.run()
