from alas_ce0.common.client_base import ApiClientBase

from alas_ce0.management.task import TaskClient


class MaintenanceClient(ApiClientBase):
    def process_operation(self, operation, params):
        return TaskClient(**self.args).enqueue('maintenance', {
            'operation': operation,
            'params': params
        })
