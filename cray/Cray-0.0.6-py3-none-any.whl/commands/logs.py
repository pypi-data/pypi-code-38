from cliff.command import Command
import cray.tasks as tasks
import logging
import sys


class Logs(Command):
    "Output logs from a given task"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Logs, self).get_parser(prog_name)
        parser.add_argument(
            "-j", "--job", nargs=1, required=True, help="Job ID", type=str, dest="job"
        )
        parser.add_argument(
            "-t",
            "--task",
            nargs=1,
            required=True,
            help="Task ID",
            type=str,
            dest="task",
        )
        return parser

    def take_action(self, parsed_args):
        jobID = parsed_args.job[0]
        taskID = parsed_args.task[0]
        self.log.debug("JobID={} Task={}".format(jobID, taskID))

        if not tasks.has_executed(jobID, taskID):
            raise Exception("Task {} has not been executed".format(taskID))

        logs = tasks.logs(jobID, taskID)
        print(logs["out"])
        print(logs["err"], file=sys.stderr)
