__author__ = "UShareSoft"

from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from ussclicore.cmd import Cmd, CoreGlobal
from texttable import Texttable
from uforgecli.utils.org_utils import org_get
from uforgecli.utils import org_utils
from ussclicore.utils import generics_utils, printer

from uforgecli.utils.uforgecli_utils import *
from uforgecli.utils import *
import shlex


class User_Admin_Cmd(Cmd, CoreGlobal):
        """User admin administration"""
        cmd_name = "admin"

        def __init__(self):
                super(User_Admin_Cmd, self).__init__()

        def arg_promote(self):
                doParser = ArgumentParser(add_help=True, description="Promote user to be an administrator of an organization (note: admin access rights are handled by roles)")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--account', dest='account', type=str, required=True, help="User name of the account to promote.")
                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization where the user is/will be a member/administrator (depending on command context). If no organization is provided, then the default organization is used.")

                return doParser

        def do_promote(self, args):
                try:
                        doParser = self.arg_promote()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)

                        adminUser = self.api.Users(doArgs.account).Get()

                        if adminUser == None:
                                printer.out("User [" + doArgs.account + "] doesn't exist.", printer.ERROR)
                                return 0
                        self.api.Orgs(org.dbId).Members(adminUser.loginName).Update(Admin=True, body=adminUser)
                        printer.out("User [" + doArgs.account + "] has been promoted in [" + org.name + "] :", printer.OK)

                        # Second API call to get latest infos
                        adminUser = self.api.Users(doArgs.account).Get()
                        if adminUser.active:
                                active = "X"
                        else:
                                active = ""

                        printer.out("Informations about ["+ adminUser.loginName+"] :")
                        table = Texttable(200)
                        table.set_cols_align(["c", "l", "c", "c", "c", "c", "c", "c"])
                        table.header(["Login", "Email", "Lastname",  "Firstname",  "Created", "Active", "Promo Code", "Creation Code"])
                        table.add_row([adminUser.loginName, adminUser.email, adminUser.surname, adminUser.firstName, adminUser.created.strftime("%Y-%m-%d %H:%M:%S"), active, adminUser.promoCode, adminUser.creationCode])
                        print table.draw() + "\n"

                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: " + str(e), printer.ERROR)
                        self.help_promote()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_promote(self):
                doParser = self.arg_promote()
                doParser.print_help()

        def arg_demote(self):
                doParser = ArgumentParser(add_help=True, description="Demote an user from being an organization administrator")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--account', dest='account', type=str, required=True, help="User name of the account to demote.")
                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization where the user is/will be a member/administrator (depending on command context). If no organization is provided, then the default organization is used.")

                return doParser

        def do_demote(self, args):
                try:
                        doParser = self.arg_demote()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)

                        adminUser = self.api.Users(doArgs.account).Get()

                        if adminUser == None:
                                printer.out("User [" + doArgs.account + "] doesn't exist.", printer.ERROR)
                                return 0
                        self.api.Orgs(org.dbId).Members(adminUser.loginName).Update(Admin=False, body=adminUser)
                        printer.out("User [" + doArgs.account + "] has been demoted in [" + org.name + "] :", printer.OK)

                        # Second API call to get latest infos
                        adminUser = self.api.Users(doArgs.account).Get()
                        if adminUser.active:
                                active = "X"
                        else:
                                active = ""

                        printer.out("Informations about ["+ adminUser.loginName+"] :")
                        table = Texttable(200)
                        table.set_cols_align(["c", "l", "c", "c", "c", "c", "c", "c"])
                        table.header(["Login", "Email", "Lastname",  "Firstname",  "Created", "Active", "Promo Code", "Creation Code"])
                        table.add_row([adminUser.loginName, adminUser.email, adminUser.surname, adminUser.firstName, adminUser.created.strftime("%Y-%m-%d %H:%M:%S"), active, adminUser.promoCode, adminUser.creationCode])
                        print table.draw() + "\n"

                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: " + str(e), printer.ERROR)
                        self.help_demote()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_demote(self):
                doParser = self.arg_demote()
                doParser.print_help()
