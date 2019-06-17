from .primitive import cli, Query
from .cli_tasks import cp
from .combinator import sequential, parallel
from pathlib import Path
from itertools import chain
from functools import partial
from ..primitives.task import TASK


class Root2Listmode(TASK):
    def __init__(self, work_directory, resources):
        if not isinstance(work_directory, Path):
            self.work_directory = work_directory
        else:
            self.work_directory = work_directory
        self.resources = resources
        self.observable = self._main()

    def _load_resources(self):
        resource_urls_in_nested_lists = list(map(Query.from_resource(), self.resources))
        resource_urls = list(chain(*resource_urls_in_nested_lists))

        cp_to_workdir = partial(cp, target=self.work_directory)

        loads_to_para = list(map(cp_to_workdir, resource_urls))

        return parallel(loads_to_para)

    def _submit(self):
        return cli("/bin/bash root2trans_h5.sh")

    def _main(self):
        return sequential([self._load_resources(), self._submit])
