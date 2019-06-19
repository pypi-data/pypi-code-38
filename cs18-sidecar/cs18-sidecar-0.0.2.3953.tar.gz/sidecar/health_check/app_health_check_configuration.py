from typing import Dict


class HealthCheckConfiguration:
    def __init__(self, script_name: str, target_ports: [], timeout_sec: int):
        self.target_ports = target_ports
        self.timeout_sec = timeout_sec
        self.script_name = script_name


class AppHealthCheckConfiguration:
    _app_health_checks: Dict[str, HealthCheckConfiguration] = {}

    def add_app_healthcheck_info(self, app_name: str, script_name: str, target_ports: [], timeout_sec: int):
        self._app_health_checks[app_name] = HealthCheckConfiguration(script_name, target_ports, timeout_sec)
        return self

    def get_configuration(self, app_name: str)->HealthCheckConfiguration:
        if app_name not in self._app_health_checks:
            raise Exception("No health-check configuration was found for app '{}'".format(app_name))
        return self._app_health_checks[app_name]
