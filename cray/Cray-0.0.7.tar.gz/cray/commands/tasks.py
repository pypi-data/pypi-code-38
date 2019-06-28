from cliff.lister import Lister
import cray.tasks as tasks
import logging


class Tasks(Lister):
    "List the tasks associated with a job"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Tasks, self).get_parser(prog_name)
        parser.add_argument(
            "-j", "--job", nargs=1, required=True, help="Job ID", type=str, dest="job"
        )
        return parser

    def take_action(self, parsed_args):
        jobID = parsed_args.job[0]
        self.log.debug("JobID={}".format(jobID))

        tt = tasks.get_job_tasks(jobID)

        return (("ID",), ((t,) for t in tt))
