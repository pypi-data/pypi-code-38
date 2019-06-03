import os

from fxq.core.stereotype import Component

from fxq.geoffrey.model import Task


@Component
class TaskRunner:

    def run_task(self, task: Task):
        for cmd in task.script_commands:
            print("Running %s" % cmd)
            os.system(cmd)
