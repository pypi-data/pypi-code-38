
__author__="UShareSoft"

from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from ussclicore.cmd import Cmd, CoreGlobal
from texttable import Texttable
from uforgecli.utils.org_utils import org_get
from ussclicore.utils import generics_utils, printer
from uforgecli.utils.uforgecli_utils import *
from uforgecli.utils import org_utils
from uforge.objects import uforge
from uforgecli.utils import *
import shlex
from uforgecli.utils.compare_utils import compare


class User_TargetPlatform_Cmd(Cmd, CoreGlobal):
        """User targetPlatform administration (list|enable|disable)"""

        cmd_name = "targetplatform"

        def __init__(self):
                super(User_TargetPlatform_Cmd, self).__init__()

        def arg_list(self):
                doParser = ArgumentParser(add_help = True, description="List all the target platform from a user.")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--account', dest='account', type=str, required=True, help="List target platforms for provided user")
                optional.add_argument('--org', dest='org', type=str, required=False, help="List target platforms for provided user by a specific organization.")

                return doParser

        def do_list(self, args):
                try:
                        doParser = self.arg_list()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)
                        if org is None:
                                printer.out("There is no organization matching ["+doArgs.org+"].", printer.OK)
                                return 0

                        printer.out("Getting target platform list for user \""+doArgs.account+"\" :")
                        if doArgs.org is not None:
                                targetPlatformsUser = self.api.Users(doArgs.account).Targetplatforms.Getall(org=org.dbId)
                        else:
                                targetPlatformsUser = self.api.Users(doArgs.account).Targetplatforms.Getall()
                        if targetPlatformsUser is None or len(targetPlatformsUser.targetPlatforms.targetPlatform) == 0:
                                printer.out("There is no target platform for the user \""+doArgs.account+"\" in [" + org.name + "].")
                                return 0
                        else:
                                targetPlatformsUser = generics_utils.order_list_object_by(targetPlatformsUser.targetPlatforms.targetPlatform, "name")
                                printer.out("Target platform list for user \""+doArgs.account+"\":")
                                table = Texttable(0)
                                table.set_cols_align(["c", "c", "c", "c"])
                                table.header(["Id", "Name", "Type", "Access"])
                                for item in targetPlatformsUser:
                                        if item.access:
                                                access = "X"
                                        else:
                                                access = ""
                                        table.add_row([item.dbId, item.name, item.type, access])
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

        def arg_enable(self):
                doParser = ArgumentParser(add_help = True, description="Enable one or more target platforms access for provided user")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--account', dest='account', type=str, required=True, help="Enable target platform for provided user")
                mandatory.add_argument('--targetPlatforms', dest='targetPlatforms', nargs='+', type=str, required=True, help="targetPlatform(s) to enable. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--org', dest='org', type=str, required=False, help="Organization where the target platform to enable is. If not entered, default organization selected.")

                return doParser

        def do_enable(self, args):
                try:
                        doParser = self.arg_enable()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)
                        if org is None:
                                printer.out("There is no organization matching ["+doArgs.org+"].", printer.OK)
                                return 0

                        targetPlatformsOrg = self.api.Orgs(org.dbId).Targetplatforms.Getall()
                        if targetPlatformsOrg is None or len(targetPlatformsOrg.targetPlatforms.targetPlatform) == 0:
                                printer.out("There is no target platform for the user \""+doArgs.account+"\" in [" + org.name + "].")
                                return 0
                        else:
                                targetPlatformsOrg = targetPlatformsOrg.targetPlatforms.targetPlatform

                                targetPlatformsList = targetPlatforms()
                                targetPlatformsList.targetPlatforms = pyxb.BIND()

                                targetPlatformsOrg = compare(targetPlatformsOrg, doArgs.targetPlatforms, "name")

                                if len(targetPlatformsOrg) == 0:
                                        listName = ""
                                        for tpname in doArgs.targetPlatforms:
                                                listName = listName + tpname + " "
                                        printer.out("There is no target platforms matching ["+listName+"].")
                                        return 0

                                for item in targetPlatformsOrg:
                                        targetPlatformToEnable = targetPlatform()
                                        targetPlatformToEnable = item
                                        targetPlatformToEnable.active = True
                                        targetPlatformToEnable.access = True
                                        printer.out("Enabling ["+item.name+"].")
                                        targetPlatformsList.targetPlatforms.append(targetPlatformToEnable)

                                result = self.api.Users(doArgs.account).Targetplatforms.Update(Org=org.name,body=targetPlatformsList)
                                result =generics_utils.order_list_object_by(result.targetPlatforms.targetPlatform, "name")

                                table = Texttable(0)
                                table.set_cols_align(["c", "c", "c", "c"])
                                table.header(["Id", "Name", "Type", "Access"])

                                for item in result:
                                        if item.access:
                                                access = "X"
                                        else:
                                                access = ""
                                        table.add_row([item.dbId, item.name, item.type, access])

                                printer.out("Target Platform list for user \""+doArgs.account+"\" :")
                                print table.draw() + "\n"
                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_enable()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_enable(self):
                doParser = self.arg_enable()
                doParser.print_help()

        def arg_disable(self):
                doParser = ArgumentParser(add_help = True, description="Disable one or more target platforms access for provided user")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--account', dest='account', type=str, required=True, help="Disable target platform for provided user")
                mandatory.add_argument('--targetPlatforms', dest='targetPlatforms', nargs='+', type=str, required=True, help="targetPlatform(s) to disable. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--org', dest='org', type=str, required=False, help="Organization where the target platform to enable is. If not entered, default organization selected.")

                return doParser

        def do_disable(self, args):
                try:
                        doParser = self.arg_disable()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)
                        if org is None:
                                printer.out("There is no organization matching ["+doArgs.org+"].", printer.OK)
                                return 0

                        if doArgs.org is not None:
                                targetPlatformsUser = self.api.Users(doArgs.account).Targetplatforms.Getall(org=org.dbId)
                        else:
                                targetPlatformsUser = self.api.Users(doArgs.account).Targetplatforms.Getall()
                        if targetPlatformsUser is None or len(targetPlatformsUser.targetPlatforms.targetPlatform) == 0:
                                printer.out("There is no target platform for the user \""+doArgs.account+"\" in [" + org.name + "].")
                                return 0
                        else:
                                targetPlatformsUser = targetPlatformsUser.targetPlatforms.targetPlatform

                                targetPlatformsList = targetPlatforms()
                                targetPlatformsList.targetPlatforms = pyxb.BIND()

                                targetPlatformsUser = compare(targetPlatformsUser, doArgs.targetPlatforms, "name")

                                if len(targetPlatformsUser) == 0:
                                        listName = ""
                                        for tpname in doArgs.targetPlatforms:
                                                listName = listName + tpname + " "
                                        printer.out("There is no target platforms matching ["+listName+"].")
                                        return 0

                                for item in targetPlatformsUser:
                                        targetPlatformToDisable = targetPlatform()
                                        targetPlatformToDisable = item
                                        targetPlatformToDisable.active = False
                                        targetPlatformToDisable.access = False
                                        printer.out("Disabling ["+item.name+"].")
                                        targetPlatformsList.targetPlatforms.append(targetPlatformToDisable)

                                result = self.api.Users(doArgs.account).Targetplatforms.Update(Org=org.name,body=targetPlatformsList)
                                result =generics_utils.order_list_object_by(result.targetPlatforms.targetPlatform, "name")

                                table = Texttable(0)
                                table.set_cols_align(["c", "c", "c", "c"])
                                table.header(["Id", "Name", "Type", "Access"])

                                for item in result:
                                        if item.access:
                                                access = "X"
                                        else:
                                                access = ""
                                        table.add_row([item.dbId, item.name, item.type, access])

                                printer.out("Target Platform list for user \""+doArgs.account+"\" :")
                                print table.draw() + "\n"
                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_disable()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_disable(self):
                doParser = self.arg_disable()
                doParser.print_help()