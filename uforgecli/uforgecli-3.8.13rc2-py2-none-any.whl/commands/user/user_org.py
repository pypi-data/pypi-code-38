
__author__="UShareSoft"

from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from ussclicore.cmd import Cmd, CoreGlobal
from texttable import Texttable
from uforgecli.utils.org_utils import org_get
from ussclicore.utils import generics_utils, printer
from uforgecli.utils.uforgecli_utils import *
from uforge.objects import uforge
from uforgecli.utils import *
import shlex



class User_Org_Cmd(Cmd, CoreGlobal):
        """Users organization administration (list/add/remove)"""

        cmd_name = "org"

        def __init__(self):
                super(User_Org_Cmd, self).__init__()

        def arg_list(self):
                doParser = ArgumentParser(add_help = True, description="List organizations for provided user")

                mandatory = doParser.add_argument_group("mandatory arguments")

                mandatory.add_argument('--account', dest='account', type=str, required=True, help="User name of the account for which the current command should be executed")
                return doParser

        def do_list(self, args):
                try:
                        doParser = self.arg_list()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        printer.out("Getting organizations list for user \""+doArgs.account+"\" :")
                        orgsUser = self.api.Users(doArgs.account).Orgs.Getall()
                        if len(orgsUser.orgs.org) is 0:
                                printer.out("["+doArgs.account+"] belongs to no organization.")
                                return 0
                        else:
                                orgsUser=generics_utils.order_list_object_by(orgsUser.orgs.org, "name")
                                printer.out("Organization list for user \""+doArgs.account+"\" :")
                                table = Texttable(200)
                                table.set_cols_align(["c", "c", "c", "c", "c", "c"])
                                table.header(["Id", "Name", "Default", "Auto Activation", "Store", "Admin"])
                                for item in orgsUser:
                                        if item.activateNewUsers:
                                                dfltActive = "X"
                                        else:
                                                dfltActive = ""
                                        if item.galleryUri is None:
                                                store = ""
                                        else:
                                                store = "X"
                                        if item.defaultOrg:
                                                default = "X"
                                        else:
                                                default = ""
                                        if item.admin:
                                                admin = "X"
                                        else:
                                                admin = ""
                                        table.add_row([item.dbId, item.name, default, dfltActive, store, admin])
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

        def arg_add(self):
                doParser = ArgumentParser(add_help = True, description="Get a user admin to the default organization or the provided one")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--account', dest='account', type=str, required=True, help="User name of the account for which the current command should be executed")

                optional.add_argument('--admin', dest='admin', action="store_true", required=False, help="Flag to provide administration privileges to the user for the organization")
                optional.add_argument('--publisher', dest='publisher', action="store_true", required=False, help="Flag to provide publish rights to the organization's App Store for the account being created.")
                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization where the user is/will be a member/administrator (depending on command context). If no organization is provided, then the default organization is used.")
                return doParser

        def do_add(self, args):
                try:
                        doParser = self.arg_add()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_get(self.api, doArgs.org)

                        printer.out("Getting \""+doArgs.account+"\" user account :")
                        userGet = self.api.Users(doArgs.account).Get()

                        printer.out("Adding Organization.")
                        self.api.Users(doArgs.account).Orgs(org.name).Change(Admin=doArgs.admin)
                        printer.out("User [" + doArgs.account + "] as been added to the organization [" + org.name + "]", printer.OK)
                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_add()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_add(self):
                doParser = self.arg_add()
                doParser.print_help()

        def arg_remove(self):
                doParser = ArgumentParser(add_help=True, description="Remove user account from the default organization or from the provided one")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--account', dest='account', type=str, required=True, help="User name of the account for which the current command should be executed")
                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization where the user is/will be a member/administrator (depending on command context). If no organization is provided, then the default organization is used.")

                return doParser

        def do_remove(self, args):
                try:
                        doParser = self.arg_remove()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_get(self.api, doArgs.org)

                        printer.out("Getting \""+doArgs.account+"\" user account :")
                        userGet = self.api.Users(doArgs.account).Get()

                        self.api.Users(doArgs.account).Orgs(org.name).Remove(None)
                        printer.out("[" + doArgs.account + "] has been removed from [" + org.name + "].", printer.OK)

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_remove()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_remove(self):
                doParser = self.arg_remove()
                doParser.print_help()