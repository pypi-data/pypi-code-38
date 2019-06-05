__author__ = "UShareSoft"

from texttable import Texttable
from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from uforgecli.utils.uforgecli_utils import *
from ussclicore.cmd import Cmd, CoreGlobal
from uforgecli.utils import org_utils
from ussclicore.utils import printer
from ussclicore.utils import generics_utils
from uforgecli.utils import uforgecli_utils
from uforgecli.utils.compare_utils import compare
import pyxb
import shlex


class Role_Entitlement_Cmd(Cmd, CoreGlobal):
        """Manage roles entitlements"""

        cmd_name = "entitlement"

        def __init__(self):
                super(Role_Entitlement_Cmd, self).__init__()

        def arg_add(self):
                doParser = ArgumentParser(prog=self.cmd_name + " add", add_help=True, description="Add one or more entitlements to a role within the specified organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--name', dest='name', required=True, help="The name of role")
                mandatory.add_argument('--entitlements', dest='entitlements', nargs='+', required=True, help="List of entitlements to add to a role. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--org', dest='org', required=False, help="The organization name. If no organization is provided, then the default organization is used.")
                return doParser

        def do_add(self, args):
                try:
                        # add arguments
                        do_parser = self.arg_add()
                        doArgs = do_parser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)

                        printer.out("Getting role [" + doArgs.name + "]...")
                        all_roles = self.api.Orgs(org.dbId).Roles().Getall(None)

                        old_role = None
                        for r in all_roles.roles.role:
                                if r.name == doArgs.name:
                                        old_role = r
                                        break

                        if old_role is None:
                                printer.out("No role [" + doArgs.name + "]...")
                                return 1

                        new_role = role()
                        new_role.name = old_role.name
                        new_role.description = old_role.description
                        new_role.entitlements = pyxb.BIND()

                        for r in old_role.entitlements.entitlement:
                                already_entitlement = entitlement()
                                already_entitlement.name = r.name
                                new_role.entitlements.append(already_entitlement)

                        entitlementsList = self.api.Entitlements.Getall()
                        entitlementsList = compare(entitlementsList.entitlements.entitlement, doArgs.entitlements, "name")

                        for e in entitlementsList:
                                new_entitlement = entitlement()
                                new_entitlement.name = e.name
                                new_role.entitlements.append(new_entitlement)
                                printer.out("Added " + new_entitlement.name + " to role.")

                        if len(entitlementsList) == 0:
                                printer.out("No entitlements found.", printer.ERROR)
                                return 0

                        self.api.Orgs(org.dbId).Roles().Update(new_role)
                        printer.out("Role [" + doArgs.name + "] updated with new entitlements.", printer.OK)
                        return 0
                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_add()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_add(self):
                do_parser = self.arg_add()
                do_parser.print_help()

        def arg_remove(self):
                doParser = ArgumentParser(prog=self.cmd_name + " remove", add_help=True, description="Remove one or more entitlements to a role within the specified organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--name', dest='name', required=True, help="the name of role")
                mandatory.add_argument('--entitlements', dest='entitlements', nargs='+', required=True, help="List of entitlements to remove to a role. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--org', dest='org', required=False, help="the organization name. If no organization is provided, then the default organization is used.")
                return doParser

        def do_remove(self, args):
                try:
                        # add arguments
                        do_parser = self.arg_remove()
                        doArgs = do_parser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        printer.out("Getting role [" + doArgs.name + "]...")
                        org = org_utils.org_get(self.api, doArgs.org)
                        all_roles = self.api.Orgs(org.dbId).Roles().Getall(None)

                        old_role = None
                        for r in all_roles.roles.role:
                                if r.name == doArgs.name:
                                        old_role = r
                                        break

                        if old_role is None:
                                printer.out("No role [" + doArgs.name + "]...")
                                return 0

                        new_role = role()
                        new_role.name = old_role.name
                        new_role.description = old_role.description
                        new_role.entitlements = pyxb.BIND()

                        delete_roles = compare(r.entitlements.entitlement, doArgs.entitlements, "name")

                        for entitlementItem in r.entitlements.entitlement:
                                exist = False
                                for deleterole in delete_roles:
                                        if entitlementItem.name == deleterole.name:
                                                exist = True
                                if not exist:
                                        already_entitlement = entitlement()
                                        already_entitlement.name = entitlementItem.name
                                        new_role.entitlements.append(already_entitlement)
                                else:
                                        printer.out("Removed " + entitlementItem.name + " from role.")

                        self.api.Orgs(org.dbId).Roles().Update(new_role)
                        printer.out("Role [" + doArgs.name + "] updated with new entitlements.", printer.OK)
                        return 0
                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_remove()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_remove(self):
                do_parser = self.arg_remove()
                do_parser.print_help()