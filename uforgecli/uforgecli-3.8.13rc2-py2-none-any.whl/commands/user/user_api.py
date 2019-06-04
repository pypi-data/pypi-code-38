__author__="UShareSoft"

from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from ussclicore.cmd import Cmd, CoreGlobal
from texttable import Texttable
from uforgecli.utils.org_utils import org_get
from ussclicore.utils import generics_utils, printer
from uforgecli.utils.uforgecli_utils import *
from uforgecli.utils import *
import shlex


class User_Api_Cmd(Cmd, CoreGlobal):
        """Set the quota of api keys the user can create"""

        cmd_name="api"

        def __init__(self):
                super(User_Api_Cmd, self).__init__()

        def arg_quota(self):
                doParser = ArgumentParser(add_help = True, description="Set the quota of api keys the user can create")

                mandatory = doParser.add_argument_group("mandatory arguments")

                mandatory.add_argument('--account', dest='account', type=str, required=True, help="User name of the account for which the current command should be executed")
                mandatory.add_argument('--apimax', dest='apimax', type=int, required=True, help="Set the maximum number of API Key pairs the user can create.")

                return doParser

        def do_quota(self, args):
                try:
                        doParser = self.arg_quota()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        user = self.api.Users(doArgs.account).Get()

                        user.apiKeysQuota = doArgs.apimax

                        user = self.api.Users(doArgs.account).Update(body=user)

                        printer.out("Quotas of api keys set at " + str(user.apiKeysQuota) + " for [" + user.name + "].", printer.OK)

                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_quota()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_quota(self):
                doParser = self.arg_quota()
                doParser.print_help()

        def arg_info(self):
                doParser = ArgumentParser(add_help = True, description="Get the quota of api keys the user can create")

                mandatory = doParser.add_argument_group("mandatory arguments")

                mandatory.add_argument('--account', dest='account', type=str, required=True, help="User name of the account for which the current command should be executed")

                return doParser

        def do_info(self, args):
                try:
                        doParser = self.arg_info()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        user = self.api.Users(doArgs.account).Get()

                        if user.apiKeysQuota is not None:
                                printer.out("Quotas of api keys set at " + str(user.apiKeysQuota) + " for [" + user.name + "].")
                        else:
                                printer.out("No api keys quota found for [" + user.name + "].")

                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_info()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_info(self):
                doParser = self.arg_info()
                doParser.print_help()