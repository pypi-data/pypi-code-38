import logging
import tempfile

from os import getenv
from cliff.command import Command

import cray.jobs as jobs


class Submit(Command):
    "Submits the current working directory to the batch processing system"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Submit, self).get_parser(prog_name)
        parser.add_argument(
            "-t",
            "--ticket",
            nargs=1,
            required=True,
            help="Jira ticket identifier",
            type=str,
            dest="ticket",
        )
        parser.add_argument(
            "-d",
            "--description",
            nargs=1,
            required=True,
            help="A description of the job",
            type=str,
            dest="desc",
        )
        parser.add_argument(
            "-s",
            "--ssh-dir",
            nargs=1,
            required=False,
            default="{}/.ssh".format(getenv("HOME")),
            help="Path to the ssh directory",
            type=str,
            dest="ssh_dir",
        )
        parser.add_argument(
            "-w",
            "--fix-windows-path",
            required=False,
            default=False,
            help="This will fix paths on windows to make them unixlike",
            dest="fix_windows_path",
            action="store_true",
        )
        parser.add_argument(
            "-c",
            "--config",
            required=False,
            default="",
            help="Path to configuration file",
            type=str,
            dest="config",
        )
        return parser

    def take_action(self, parsed_args):
        ticket = parsed_args.ticket[0]
        desc = parsed_args.desc[0].replace(" ", "_")
        jobID = "{}#{}".format(ticket, desc)
        ssh_dir = parsed_args.ssh_dir[0]
        fix_windows_path = parsed_args.fix_windows_path
        config = parsed_args.config
        self.log.debug("Ticket={} Desc={} JobID={}".format(ticket, desc, jobID))

        if jobs.exists(jobID):
            raise Exception("Duplicate job: '{}'".format(jobID))

        with tempfile.TemporaryDirectory() as tempdir:
            jobs.build_job_archive(tempdir, config, ssh_dir, fix_windows_path)
            jobs.submit_job_zip("{}/job.zip".format(tempdir), jobID)

        self.log.info("Created job {}".format(jobID))
