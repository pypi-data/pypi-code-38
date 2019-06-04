__author__ = "UShareSoft"

import shlex

from uforgecli.utils.texttable_utils import *
from uforgecli.utils.uforgecli_utils import *
from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from ussclicore.cmd import Cmd, CoreGlobal
from ussclicore.utils import printer

from uforgecli.utils import org_utils

class Org_Repo_Refresh_Cmd(Cmd, CoreGlobal):
    """Repository refresh operations (trigger|status|list)"""

    cmd_name = "refresh"

    def __init__(self):
        super(Org_Repo_Refresh_Cmd, self).__init__()

    def arg_trigger(self):
        doParser = ArgumentParser(add_help=True, description="Trigger a refresh for a repository in the organization")

        mandatory = doParser.add_argument_group("mandatory arguments")
        optional = doParser.add_argument_group("optional arguments")

        mandatory.add_argument("--repoId", dest="repoId", type=str, required=True, help="Id of the repository")
        optional.add_argument("--org", dest="org", type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")

        return doParser

    def do_trigger(self, args):
        try:
            doParser = self.arg_trigger()
            doArgs = doParser.parse_args(shlex.split(args))

            # if the help command is called, parse_args returns None object
            if not doArgs:
                return 2

            repository_update = self._trigger(doArgs.org, doArgs.repoId)

            self._print("Refresh successfully triggered with id '{0}' for repository '{1}'".format(str(repository_update.dbId), str(doArgs.repoId)), printer.OK)

            return 0
        except ArgumentParserError as e:
            self._print("In Arguments: " + str(e), printer.ERROR)
            self.help_trigger()
        except Exception as e:
            return handle_uforge_exception(e)

    def _trigger(self, org_name, repo_id):
        org = org_utils.org_get(self.api, org_name)
        return self.api.Orgs(org.dbId).Repositories(repo_id).Updates.Create()

    def help_trigger(self):
        doParser = self.arg_trigger()
        doParser.print_help()

    def arg_status(self):
        doParser = ArgumentParser(add_help=True, description="Retrieve the status for the given refresh in the organization")

        mandatory = doParser.add_argument_group("mandatory arguments")
        optional = doParser.add_argument_group("optional arguments")

        mandatory.add_argument("--repoId", dest="repoId", type=str, required=True, help="Id of the repository")
        mandatory.add_argument("--refreshId", dest="refreshId", type=str, required=True, help="Id of the refresh")
        optional.add_argument("--org", dest="org", type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")

        return doParser

    def do_status(self, args):
        try:
            doParser = self.arg_status()
            doArgs = doParser.parse_args(shlex.split(args))

            # if the help command is called, parse_args returns None object
            if not doArgs:
                return 2

            status = self._get_status(doArgs.org, doArgs.repoId, doArgs.refreshId)

            message = "Status of the refresh '{0}': ".format(doArgs.refreshId)
            if status is "":
                message += "Pending..."
            else:
                message += "{0} ({1}%)".format(status.message, str(status.percentage))
            self._print(message, printer.OK)

            return 0
        except ArgumentParserError as e:
            self._print("In Arguments: " + str(e), printer.ERROR)
            self.help_status()
        except Exception as e:
            return handle_uforge_exception(e)

    def _get_status(self, org_name, repo_id, refresh_id):
        org = org_utils.org_get(self.api, org_name)
        return self.api.Orgs(org.dbId).Repositories(repo_id).Updates(refresh_id).Status.Get()

    def help_status(self):
        doParser = self.arg_status()
        doParser.print_help()

    def arg_list(self):
        doParser = ArgumentParser(add_help=True, description="List last refreshes triggered for a repository in the organization")

        mandatory = doParser.add_argument_group("mandatory arguments")
        optional = doParser.add_argument_group("optional arguments")

        mandatory.add_argument("--repoId", dest="repoId", type=str, required=True, help="Id of the repository")
        optional.add_argument("--org", dest="org", type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")
        optional.add_argument("--count", dest="count", type=long, required=False, help="The number of refreshes to display. If none provided, assume 10. To display all, use '--count 0'.", default=10)

        return doParser

    def do_list(self, args):
        try:
            doParser = self.arg_list()
            doArgs = doParser.parse_args(shlex.split(args))

            # if the help command is called, parse_args returns None object
            if not doArgs:
                return 2

            repository_updates = self._get_repository_updates(doArgs.org, doArgs.repoId, doArgs.count)

            table = init_texttable(["Id", "Created", "Status"],
                                   200,
                                   ["l", "l", "l"],
                                   ["t", "a", "t"])

            # have to reverse order because REST call returns last refreshes first, to allow pagination
            for repository_update in reversed(repository_updates):
                if repository_update.status is None:
                    status = "Pending..."
                else:
                    status = repository_update.status.message
                table.add_row([repository_update.dbId, repository_update.created.strftime("%Y-%m-%d %H:%M:%S"), status])

            count_str = str(doArgs.count) + " "
            if doArgs.count == 0:
                count_str = ""
            self._print("Last {0}refreshes for repository '{1}':".format(count_str, doArgs.repoId), printer.OK)
            self._print(table.draw())

            return 0
        except ArgumentParserError as e:
            self._print("In Arguments: " + str(e), printer.ERROR)
            self.help_list()
        except Exception as e:
            return handle_uforge_exception(e)

    def _get_repository_updates(self, org_name, repo_id, count):
        org = org_utils.org_get(self.api, org_name)
        return self.api.Orgs(org.dbId).Repositories(repo_id).Updates.Getall(Count=count, Orderby="created", Descending=True).repositoryUpdates.repositoryUpdate

    def help_list(self):
        doParser = self.arg_list()
        doParser.print_help()

    def _print(self, message, level=""):
        printer.out(message, level)