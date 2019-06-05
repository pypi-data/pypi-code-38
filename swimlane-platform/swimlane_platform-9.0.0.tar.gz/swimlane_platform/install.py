import subprocess
import sys
from os import path
import os
import stat
from swimlane_platform.lib import ValidationException, ArgsConfigQuestions, info_function_start_finish, Configuration, \
    BaseWithLog, names, DockerComposeManager
from swimlane_platform.enable_ssl import run as run_enable_ssl
from swimlane_platform.add_file_encryption_key import run as run_add_file_encryption


def find_remote_sibling(location, name):
    folder = path.join(location, name)
    if path.exists(folder):
        return folder
    elif location == '/':
        return None
    else:
        return find_remote_sibling(path.dirname(location), name)


class SwimlaneInstaller(BaseWithLog):

    def __init__(self, args):
        # type: (Configuration) -> None
        super(SwimlaneInstaller, self).__init__(args)

    @info_function_start_finish('Install Swimlane.')
    def run(self):
        """
        Main Swimlane install method.
        """
        self.run_old_script()
        run_enable_ssl(self.args.to_dict())
        run_add_file_encryption(self.args.to_dict())
        self.run_after_install()

    def run_old_script(self):
        """
        Runs old installation script.
        """
        script_path = path.dirname(path.realpath(__file__))
        install_script = path.join(find_remote_sibling(script_path, 'swimlane_scripts'), 'install.sh')
        if not install_script:
            raise ValidationException('Script file not found.')
        st = os.stat(install_script)
        os.chmod(install_script, st.st_mode | stat.S_IEXEC)
        install_template_folder = find_remote_sibling(script_path, 'swimlane_template_dir')
        commands = [install_script, '--install-template-folder', install_template_folder]
        system_args = sys.argv[1:] if len(sys.argv) > 1 else []
        commands.extend(system_args)
        if self.args.log and '--log' not in system_args:
            commands.extend(['--log', self.args.log])
        if self.args.dev and '--dev' not in system_args:
            commands.append('--dev')
        subprocess.check_output(commands)

    def run_after_install(self):
        # type: () -> None
        """
        Prompts the user and starts or leaves containers as is.
        """
        questions = [{
            'type': 'confirm',
            'name': 'start_swimlane',
            'message': 'Would you like to start the Swimlane services?'
        }]
        config_manager = ArgsConfigQuestions(self.args.to_dict())
        config_manager.collect(questions)
        args = config_manager.to_arguments()
        if args.start_swimlane:
            docker_compose_file = path.join(names.INSTALL_DIR, names.DOCKER_COMPOSE_FILE)
            DockerComposeManager(self.logger, docker_compose_file).docker_compose_up()
        else:
            self.logger.info('To start the Swimlane Services manually, cd /opt/swimlane and run "docker-compose up -d".')


def run(parent_config):
    # type: (ArgsConfigQuestions) -> None
    installer = SwimlaneInstaller(parent_config.to_arguments())
    installer.run()
