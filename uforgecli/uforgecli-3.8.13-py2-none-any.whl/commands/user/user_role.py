__author__ = "UShareSoft"

from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from ussclicore.cmd import Cmd, CoreGlobal
from texttable import Texttable
from uforgecli.utils.org_utils import org_get
from ussclicore.utils import generics_utils, printer
from uforgecli.utils.uforgecli_utils import *
from uforgecli.utils.compare_utils import *
from uforge.objects import uforge
import pyxb
import shlex


class User_Role_Cmd(Cmd, CoreGlobal):
        """Manage users' roles"""

        cmd_name = "role"

        def __init__(self):
                super(User_Role_Cmd, self).__init__()

        def arg_list(self):
                do_parser = ArgumentParser(prog=self.cmd_name + " list", add_help=True, description="Display the current list of roles for the user")

                mandatory = do_parser.add_argument_group("mandatory arguments")
                optional = do_parser.add_argument_group("optional arguments")

                mandatory.add_argument('--account', dest='account', required=True, help="User name of the account for which the current command should be executed")

                optional.add_argument('--org', dest='org', required=False, help="The organization name. If no organization is provided, then the default organization is used.")
                return do_parser

        def do_list(self, args):
                try:
                        doParser = self.arg_list()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        printer.out("Getting roles and their entitlements for user [" + doArgs.account + "]:\n")
                        roles = self.api.Users(doArgs.account).Roles.Getall()

                        table = Texttable(200)
                        table.set_cols_align(["l", "l"])
                        table.header(["Name", "Description"])
                        table.set_cols_width([30,60])
                        for role in roles.roles.role:
                                table.add_row([role.name, role.description])
                                for entitlement in role.entitlements.entitlement:
                                        table.add_row(["===> " + entitlement.name, entitlement.description])

                        printer.out("Role entitlements are represented with \"===>\".", printer.INFO)
                        print table.draw() + "\n"
                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_list()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_list(self):
                do_parser = self.arg_list()
                do_parser.print_help()

        def arg_add(self):
                do_parser = ArgumentParser(prog=self.cmd_name + " add", add_help=True, description="Add one or more roles to the user (note the role(s) must exist in the organization where the user is a member)")

                mandatory = do_parser.add_argument_group("mandatory arguments")
                optional = do_parser.add_argument_group("optional arguments")

                mandatory.add_argument('--account', dest='account', required=True, help="user name of the account for which the current command should be executed")
                mandatory.add_argument('--roles', dest='roles', nargs='+', required=True, help="a list of roles to be added to this user (example: --roles role1 role2 role3). For a list of available roles, run the command: uforge role list --org <org name>")

                optional.add_argument('--org', dest='org', required=False, help="the organization name. If no organization is provided, then the default organization is used.")
                return do_parser

        def do_add(self, args):
                try:
                        doParser = self.arg_add()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        # call UForge API
                        printer.out("Getting user [" + doArgs.account + "] ...")
                        user = self.api.Users(doArgs.account).Get()

                        if user is None:
                                printer.out("user " + self.login + "does not exist", printer.ERROR)
                                return 0

                        org = org_get(self.api, doArgs.org)
                        orgRoles = self.api.Orgs(org.dbId).Roles().Getall(body=None)

                        # Check if the given roles really exist in the organization
                        if doArgs.roles != None:
                                checkedRoleList = []
                                for r in doArgs.roles:
                                        found = False
                                        for existing_role in orgRoles.roles.role:
                                                if existing_role.name == r:
                                                        found = True
                                                        checkedRoleList.append(r)
                                                        break
                                        if found == False:
                                                printer.out("Unable to find role with name [" + r + "] in organization [" + org.name + "]", printer.ERROR)
                                                return 0

                                # Create a new roles structures
                                new_roles = roles()
                                new_roles.roles = pyxb.BIND()

                                # Add the new roles
                                for new_role in checkedRoleList:
                                        r = role()
                                        r.name = new_role
                                        new_roles.roles.append(r)
                                # Add the user existing roles
                                for existing_user_role in user.roles.role:
                                        new_roles.roles.append(existing_user_role)

                                self.api.Users(doArgs.account).Roles.Update(new_roles)
                                printer.out("User [" + doArgs.account + "] updated with new roles.", printer.OK)
                        else:
                                printer.out("You need to specify roles to add.", printer.ERROR)

                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_add()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_add(self):
                do_parser = self.arg_add()
                do_parser.print_help()

        def arg_remove(self):
                do_parser = ArgumentParser(prog=self.cmd_name + " remove", add_help=True, description="Remove one or more entitlements to a role within the specified organization")

                mandatory = do_parser.add_argument_group("mandatory arguments")

                mandatory.add_argument('--account', dest='account', required=True, help="user name of the account for which the current command should be executed")
                mandatory.add_argument('--roles', dest='roles', nargs='+', required=True, help="a list of roles to be removed (example: --roles role1 role2 role3).")
                return do_parser

        def do_remove(self, args):
                try:
                        doParser = self.arg_remove()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        # Call to UForge API
                        printer.out("Getting user [" + doArgs.account + "] ...")
                        user = self.api.Users(doArgs.account).Get()
                        if doArgs.roles != None:
                                new_roles = roles()
                                new_roles.roles = pyxb.BIND()

                                for r in user.roles.role:
                                        if r.name not in doArgs.roles:
                                                already_role = role()
                                                already_role.name = r.name
                                                new_roles.roles.append(already_role)

                                self.api.Users(doArgs.account).Roles.Update(new_roles)
                                printer.out("User [" + doArgs.account + "] roles updated.", printer.OK)
                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_remove()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_remove(self):
                do_parser = self.arg_remove()
                do_parser.print_help()
