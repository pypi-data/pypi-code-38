import rx
from pathlib import Path
from rx import operators as ops

from ..backend.azure import AzureBatch
from ..primitives.resources import FileResource
from .monte_carlo_v2 import MonteCarloBase
from .cli_tasks import CLI


class MonteCarloOnAzure(MonteCarloBase):
    def __init__(
        self,
        backend,
        target_mac,
        nb_splits,
        spec={},
        result_dir="simu_result",
        resources=FileResource("/mnt/deployment/monte_carlo_simu_common_resources"),
    ):
        super().__init__(target_mac, nb_splits, spec, result_dir, resources)
        self.backend = backend

    def on_create(self):
        return rx.of(self.master_task_dir).pipe(ops.flat_map(CLI.mkdir))

    def on_submit(self):
        for i in range(self.nb_splits):
            self.backend.submit_single_task()
