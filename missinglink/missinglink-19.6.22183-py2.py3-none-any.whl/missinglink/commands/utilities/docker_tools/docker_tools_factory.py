# -*- coding: utf-8 -*-

from missinglink.commands.utils import is_windows
from missinglink.commands.utilities.docker_tools.docker_tools import DockerTools
from missinglink.commands.utilities.docker_tools.windows_docker_tools import WindowsDockerTools


def create_docker_tools(ctx, **kwargs):
    return WindowsDockerTools(ctx, **kwargs) if is_windows() else DockerTools(ctx, **kwargs)
