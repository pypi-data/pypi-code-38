from logging import Logger

import time
from typing import List

from sidecar.const import Const
from sidecar.file_system import FileSystemService
from sidecar.health_check.app_health_check_configuration import AppHealthCheckConfiguration
from sidecar.utils import CallsLogger


class HealthCheckPreparer:
    def __init__(self,
                 file_system: FileSystemService,
                 logger: Logger,
                 health_check_configuration: AppHealthCheckConfiguration):
        self.health_check_configuration = health_check_configuration
        self._file_system = file_system
        self._logger = logger

    def prepare(self, app_name: str, address: str):
        health_check_configuration = self.health_check_configuration.get_configuration(app_name)
        target_ports = health_check_configuration.target_ports
        if target_ports:
            app_dir = Const.get_app_folder(app_name=app_name)
            self._file_system.create_folder(app_dir)
            return self._create_default_health_check_script(default_ports=target_ports,
                                                            address=address,
                                                            app_name=app_name)

        script_file_path = Const.get_health_check_file(app_name=app_name,
                                                       script_name=health_check_configuration.script_name)
        return ['{script_file_path} {ip_address}'.format(
            script_file_path=script_file_path,
            ip_address=address)]

    @CallsLogger.wrap
    def _create_default_health_check_script(self,
                                            default_ports: List[str],
                                            app_name: str,
                                            address: str):
        script_file_path = Const.get_health_check_file(app_name=app_name,
                                                       script_name="default-{0}-hc-{1}.sh".
                                                       format(app_name, str(time.time())))
        lines = list()

        lines.append('#!/bin/bash\n')
        lines.append('ip=$1\n')
        for port_to_test in default_ports:
            lines.append(
                "echo 'Testing connectivity to port: {0} on private ip {1}'\n".format(str(port_to_test), address))
            lines.append(
                'until bash -c "</dev/tcp/$ip/{0}"; [[ "$?" -eq "0" ]];\n'.format(str(port_to_test)))
            lines.append('   do sleep 5;\n')
            lines.append(
                "echo 'Testing connectivity to port: {0} on private ip {1}'\n".format(str(port_to_test), address))
            lines.append('done;\n')
            lines.append("echo 'tested port {0}'\n".format(str(port_to_test)))
        self._file_system.write_lines_to_file(path=script_file_path, lines=lines, chmod=0o777)
        return ['{script_file_path} {ip_address}'.format(
            script_file_path=script_file_path,
            ip_address=address)]