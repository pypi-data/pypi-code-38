import threading
from typing import List

from sidecar.model.objects import ISidecarService


class ServiceStatus:
    PENDING = "Pending"
    SETUP = "Setup"
    DONE = "Done"
    SETUP_FAILED = "SetupFailed"
    ABORTED = "Aborted"
    TERMINATING = "Terminating"
    TERMINATE_FAILED = "TerminateFailed"
    TERMINATED = "Terminated"


class ServiceStatusState:

    def __init__(self, services: List[ISidecarService]):
        self._lock = threading.RLock()
        self._service_statuses = {service.name: ServiceStatus.PENDING for service in services}

    def execution_done(self, names: List[str]) -> bool:
        with self._lock:
            for name in names:
                if self._service_statuses[name] not in [ServiceStatus.DONE]:
                    return False
            return True

    def update_status(self, name: str, status: str):
        with self._lock:
            self._service_statuses[name] = status
