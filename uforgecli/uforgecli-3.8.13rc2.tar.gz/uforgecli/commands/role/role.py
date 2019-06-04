__author__ = "UShareSoft"

from texttable import Texttable
from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from ussclicore.cmd import Cmd, CoreGlobal
from ussclicore.utils.generics_utils import *
from uforgecli.utils import org_utils
from ussclicore.utils import printer
#from role_entitlements import RoleEntitlementCmds
from uforgecli.utils.uforgecli_utils import *
from uforgecli.utils.org_utils import org_get
from role_entitlement import Role_Entitlement_Cmd
from uforge.objects import uforge
from uforgecli.utils.compare_utils import compare
import shlex


class Role_Cmd(Cmd, CoreGlobal):
        """Manage platform roles"""

        cmd_name = "role"

        def __init__(self):
                self.subCmds = {}
                self.generate_sub_commands()
                super(Role_Cmd, self).__init__()

        def generate_sub_commands(self):
                roleEntitlement = Role_Entitlement_Cmd()
                self.subCmds[roleEntitlement.cmd_name] = roleEntitlement

        def arg_list(self):
                doParser = ArgumentParser(prog=self.cmd_name + " list", add_help=True, description="List all the roles for a given organization.  If not organization is provided the default organization is used.")

                optional = doParser.add_argument_group("optional arguments")

                optional.add_argument('--org', dest='org', required=False, help="The organization name. If no organization is provided, then the default organization is used.")
                return doParser

        def do_list(self, args):
                try:
                        doParser = self.arg_list()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)

                        printer.out("Getting all the roles for the organization...")
                        Roles = self.api.Orgs(org.dbId).Roles().Getall(body=None)

                        table = Texttable(200)
                        table.set_cols_align(["l", "l"])
                        table.header(["Name", "Description"])
                        table.set_cols_width([30, 60])
                        for role in Roles.roles.role:
                                table.add_row([role.name, role.description])
                        print table.draw() + "\n"
                        return 0
                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_list()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_list(self):
                doParser = self.arg_list()
                doParser.print_help()

        def arg_info(self):
                doParser = ArgumentParser(prog=self.cmd_name + " info", add_help=True, description="Prints out all the details of a specified role within an organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--name', dest='name', required=True, help="Name of the role.")
                optional.add_argument('--org', dest='org', required=False, help="The organization name. If no organization is provided, then the default organization is used.")
                return doParser

        def do_info(self, args):
                try:
                        doParser = self.arg_info()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)

                        printer.out("Getting role [" + doArgs.name + "]...")
                        all_roles = self.api.Orgs(org.dbId).Roles().Getall(None)

                        selected_role = None
                        for role in all_roles.roles.role:
                                if role.name == doArgs.name:
                                        selected_role = role
                                        break

                        if selected_role is None:
                                printer.out("No role [" + doArgs.name + "]...")
                                return 0

                        printer.out("Name: " + selected_role.name)
                        if selected_role.description is None:
                                printer.out("Description : None")
                        else:
                                printer.out("Description: " + selected_role.description)
                        if len(selected_role.entitlements.entitlement) > 0:
                                table = Texttable(200)
                                table.set_cols_align(["l", "l"])
                                table.header(["Entitlement", "Description"])
                                table.set_cols_width([30, 60])
                                for entitlement in selected_role.entitlements.entitlement:
                                        table.add_row([entitlement.name, entitlement.description])
                                print table.draw() + "\n"
                        else:
                                printer.out("There is no entitlements in this role.")

                        return 0
                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_info()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_info(self):
                doParser = self.arg_info()
                doParser.print_help()

        def arg_create(self):
                doParser = ArgumentParser(prog=self.cmd_name + " create", add_help=True, description="Create a new empty role in the specified organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--name', dest='name', required=True, help="The name of the role to create.")
                optional.add_argument('--description', dest='description', required=False, help="A role description for which the current command should be executed.")
                optional.add_argument('--entitlements', dest='entitlements', nargs='+', required=False, help="A list of entitlements to be added to this role during creation. For a list of available entitlements, run \"uforge entitlement list --org <org name>\". You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--org', dest='org', required=False, help="The organization name. If no organization is provided, then the default organization is used.")
                return doParser

        def do_create(self, args):
                try:
                        # add arguments
                        doParser = self.arg_create()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        printer.out("Creating role [" + doArgs.name + "] ...")
                        org = org_utils.org_get(self.api, doArgs.org)

                        new_role = role()
                        new_role.name = doArgs.name
                        if doArgs.description:
                                new_role.description = doArgs.description
                        if doArgs.entitlements:
                                if doArgs.entitlements is not None:
                                        new_role.entitlements = pyxb.BIND()
                                        entList = self.api.Entitlements.Getall()
                                        entList = entList.entitlements.entitlement
                                        entList = compare(entList, doArgs.entitlements, "name")
                                        for ent in entList:
                                                add_entitlement = entitlement()
                                                add_entitlement.name = ent.name
                                                add_entitlement.description = ent.description
                                                new_role.entitlements.append(add_entitlement)
                                                printer.out("Entitlement " + ent.name + " added to the role")

                        self.api.Orgs(org.dbId).Roles().Create(new_role)
                        printer.out("Role [" + new_role.name + "] was correctly created", printer.OK)
                        return 0
                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_create()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_create(self):
                doParser = self.arg_create()
                doParser.print_help()

        def arg_delete(self):
                doParser = ArgumentParser(prog=self.cmd_name + " delete", add_help=True, description="Delete a role from the specified organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--names', dest='name', nargs='+', required=True, help="Name of the role(s) separated by spaces")
                optional.add_argument('--org', dest='org', required=False, help="The organization name. If no organization is provided, then the default organization is used.")
                return doParser

        def do_delete(self, args):
                try:
                        # add arguments
                        doParser = self.arg_delete()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)

                        for role in doArgs.name:
                                self.api.Orgs(org.dbId).Roles(role).Delete()
                                printer.out("Role [" + role + "] deleted")

                        printer.out("Role(s) have been deleted successfully", printer.OK)
                        return 0

                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_delete()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_delete(self):
                doParser = self.arg_delete()
                doParser.print_help()
