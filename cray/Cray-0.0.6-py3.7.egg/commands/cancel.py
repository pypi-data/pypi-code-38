from cliff.command import Command
import cray.jobs as jobs
import logging


class Cancel(Command):
    "Cancels a job"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Cancel, self).get_parser(prog_name)
        parser.add_argument(
            "-j", "--job", nargs=1, required=True, help="Job ID", type=str, dest="job"
        )
        return parser

    def take_action(self, parsed_args):
        jobID = parsed_args.job[0]
        self.log.debug("JobID={}".format(jobID))

        if jobs.is_job_cancelled(jobID):
            raise Exception("Already cancelled: '{}'".format(jobID))

        if not jobs.is_job_active(jobID):
            raise Exception("Unknown job: '{}'".format(jobID))

        jobs.cancel_job(jobID)

        self.log.info("Job {} cancelled".format(jobID))
