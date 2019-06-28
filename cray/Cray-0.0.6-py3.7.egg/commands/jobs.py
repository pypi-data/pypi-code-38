from cliff.lister import Lister
import cray.jobs as jobs
import logging


class Jobs(Lister):
    "List the jobs within the system"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Jobs, self).get_parser(prog_name)
        parser.add_argument(
            "-t",
            "--ticket",
            nargs=1,
            required=False,
            help="Jira ticket identifier",
            type=str,
            dest="ticket",
            default="",
        )
        return parser

    def take_action(self, parsed_args):
        if parsed_args.ticket is not "":
            jj = jobs.get_ticket_jobs(parsed_args.ticket[0])
        else:
            jj = jobs.get_jobs()

        return (("ID",), ((j,) for j in jj))
