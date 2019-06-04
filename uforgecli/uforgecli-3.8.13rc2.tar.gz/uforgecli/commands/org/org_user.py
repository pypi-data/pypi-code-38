__author__ = "UShareSoft"

from texttable import Texttable
from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from uforgecli.utils.uforgecli_utils import *
from ussclicore.cmd import Cmd, CoreGlobal
from uforgecli.utils import org_utils
from ussclicore.utils.generics_utils import order_list_object_by
from ussclicore.utils import printer
from uforge.objects import uforge
from ussclicore.utils import generics_utils
from uforgecli.utils import uforgecli_utils
import pyxb
import datetime
import shlex

class Org_User_Cmd(Cmd, CoreGlobal):
        """User operation (list)"""

        cmd_name = "user"

        def __init__(self):
                super(Org_User_Cmd, self).__init__()

        def arg_list(self):
                doParser = ArgumentParser(add_help = True, description="List all the members of the provided organization")

                optional = doParser.add_argument_group("optional arguments")

                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")

                return doParser

        def do_list(self, args):
                try:
                        doParser = self.arg_list()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)
                        printer.out("Getting user list for ["+org.name+"] . . .")
                        allUsers = self.api.Orgs(org.dbId).Members.Getall()
                        allUsers = order_list_object_by(allUsers.users.user, "loginName")

                        table = Texttable(200)
                        table.set_cols_align(["l", "l", "l", "c"])
                        table.header(["Id", "Login", "Email", "Active"])

                        for item in allUsers:
                                if item.active:
                                        active = "X"
                                else:
                                        active = ""
                                table.add_row([item.dbId, item.loginName, item.email, active])

                        print table.draw() + "\n"
                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_list()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_list(self):
                doParser = self.arg_list()
                doParser.print_help()