from os import path
import subprocess
from swimlane_platform.lib.debug_decorators import debug_function_args, debug_function_return
from swimlane_platform.lib.logger import SplitStreamLogger


class DockerComposeManager:

    def __init__(self, logger, docker_compose_file):
        # type: (SplitStreamLogger, str) -> None
        self.logger = logger
        self.docker_compose_file = docker_compose_file

    @debug_function_return
    @debug_function_args
    def docker_compose_run(self, command, *args):
        # type: (str, str) -> str
        """
        Runs docker compose commands.
        :param command: Docker compose command. (up, down, build etc)
        :param args: Command arguments
        """
        command_args = ['docker-compose']
        dir_name, file_name = path.split(self.docker_compose_file)
        command_args.extend(['-f', file_name])
        command_args.append(command)
        if args:
            command_args.extend(args)
        std_out = subprocess.check_output(command_args, cwd=dir_name)
        self.logger.verbose(std_out)
        return std_out

    @debug_function_return
    def docker_compose_down(self):
        # type: () -> str
        """
        Spins down services from docker compose.
        """
        return self.docker_compose_run('down')

    @debug_function_return
    def docker_compose_up(self):
        # type: () -> str
        """
        Starts services from docker compose.
        """
        return self.docker_compose_run('up', '-d')
