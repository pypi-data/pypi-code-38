
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


class User_TargetFormat_Cmd(Cmd, CoreGlobal):
        """User targetFormat administration (list|enable|disable)"""

        cmd_name = "targetformat"

        def __init__(self):
                super(User_TargetFormat_Cmd, self).__init__()

        def arg_list(self):
                doParser = ArgumentParser(add_help = True, description="List all the target format from a user.")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--account', dest='account', type=str, required=True, help="List target formats for provided user")
                optional.add_argument('--org', dest='org', type=str, required=False, help="List target formats for provided user by a specific organization.")

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

                        printer.out("Getting target format list for user \""+doArgs.account+"\" :")
                        if doArgs.org is not None:
                                targetFormatsUser = self.api.Users(doArgs.account).Targetformats.Getall(org=org.dbId)
                        else:
                                targetFormatsUser = self.api.Users(doArgs.account).Targetformats.Getall()
                        if targetFormatsUser is None or len(targetFormatsUser.targetFormats.targetFormat) == 0:
                                printer.out("There is no target format for the user \""+doArgs.account+"\" in [" + org.name + "].")
                                return 0
                        else:
                                targetFormatsUser = generics_utils.order_list_object_by(targetFormatsUser.targetFormats.targetFormat, "name")
                                printer.out("Target format list for user \""+doArgs.account+"\":")
                                table = Texttable(200)
                                table.set_cols_align(["c", "l", "l", "l", "l", "l", "c"])
                                table.header(["Id", "Name", "Format", "Category", "Type", "CredAccountType", "Access"])
                                for item in targetFormatsUser:
                                        if item.access:
                                                access = "X"
                                        else:
                                                access = ""
                                        if item.credAccountType is None:
                                                credAccountType = ""
                                        else:
                                                credAccountType = item.credAccountType
                                        table.add_row([item.dbId, item.name, item.format.name, item.category.name, item.type, credAccountType, access])
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
                doParser = ArgumentParser(add_help = True, description="Enable one or more target formats access for provided user")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--account', dest='account', type=str, required=True, help="Enable target format for provided user")
                mandatory.add_argument('--targetFormats', dest='targetFormats', nargs='+', type=str, required=True, help="targetFormat(s) to enable. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--org', dest='org', type=str, required=False, help="Organization where the target format to enable is. If not entered, default organization selected.")

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

                        targetFormatsOrg = self.api.Orgs(org.dbId).Targetformats.Getall()
                        if targetFormatsOrg is None or len(targetFormatsOrg.targetFormats.targetFormat) == 0:
                                printer.out("There is no target format for the user \""+doArgs.account+"\" in [" + org.name + "].")
                                return 0
                        else:
                                targetFormatsOrg = targetFormatsOrg.targetFormats.targetFormat

                                targetFormatsList = targetFormats()
                                targetFormatsList.targetFormats = pyxb.BIND()

                                targetFormatsOrg = compare(targetFormatsOrg, doArgs.targetFormats, "name")

                                if len(targetFormatsOrg) == 0:
                                        listName = ""
                                        for tfname in doArgs.targetFormats:
                                                listName = listName + tfname + " "
                                        printer.out("There is no target formats matching ["+listName+"].")
                                        return 0

                                for item in targetFormatsOrg:
                                        targetFormatToEnable = targetFormat()
                                        targetFormatToEnable = item
                                        targetFormatToEnable.active = True
                                        targetFormatToEnable.access = True
                                        printer.out("Enabling ["+item.name+"].")
                                        targetFormatsList.targetFormats.append(targetFormatToEnable)

                                result = self.api.Users(doArgs.account).Targetformats.Update(Org=org.name,body=targetFormatsList)
                                result =generics_utils.order_list_object_by(result.targetFormats.targetFormat, "name")

                                table = Texttable(200)
                                table.set_cols_align(["c", "l", "l", "l", "l", "l", "c"])
                                table.header(["Id", "Name", "Format", "Category", "Type", "CredAccountType", "Access"])

                                for item in result:
                                        if item.access:
                                                access = "X"
                                        else:
                                                access = ""
                                        if item.credAccountType is None:
                                                credAccountType = ""
                                        else:
                                                credAccountType = item.credAccountType
                                        table.add_row([item.dbId, item.name, item.format.name, item.category.name, item.type, credAccountType, access])

                                printer.out("Target Format list for user \""+doArgs.account+"\" :")
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
                doParser = ArgumentParser(add_help = True, description="Disable one or more target formats access for provided user")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--account', dest='account', type=str, required=True, help="Disable target format for provided user")
                mandatory.add_argument('--targetFormats', dest='targetFormats', nargs='+', type=str, required=True, help="targetFormat(s) to disable. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--org', dest='org', type=str, required=False, help="Organization where the target format to enable is. If not entered, default organization selected.")

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
                                targetFormatsUser = self.api.Users(doArgs.account).Targetformats.Getall(org=org.dbId)
                        else:
                                targetFormatsUser = self.api.Users(doArgs.account).Targetformats.Getall()
                        if targetFormatsUser is None or len(targetFormatsUser.targetFormats.targetFormat) == 0:
                                printer.out("There is no target format for the user \""+doArgs.account+"\" in [" + org.name + "].")
                                return 0
                        else:
                                targetFormatsUser = targetFormatsUser.targetFormats.targetFormat

                                targetFormatsList = targetFormats()
                                targetFormatsList.targetFormats = pyxb.BIND()

                                targetFormatsUser = compare(targetFormatsUser, doArgs.targetFormats, "name")

                                if len(targetFormatsUser) == 0:
                                        listName = ""
                                        for tfname in doArgs.targetFormats:
                                                listName = listName + tfname + " "
                                        printer.out("There is no target formats matching ["+listName+"].")
                                        return 0

                                for item in targetFormatsUser:
                                        targetFormatToDisable = targetFormat()
                                        targetFormatToDisable = item
                                        targetFormatToDisable.active = False
                                        targetFormatToDisable.access = False
                                        printer.out("Disabling ["+item.name+"].")
                                        targetFormatsList.targetFormats.append(targetFormatToDisable)

                                result = self.api.Users(doArgs.account).Targetformats.Update(Org=org.name,body=targetFormatsList)
                                result =generics_utils.order_list_object_by(result.targetFormats.targetFormat, "name")

                        table = Texttable(200)
                        table.set_cols_align(["c", "l", "l", "l", "l", "l", "c"])
                        table.header(["Id", "Name", "Format", "Category", "Type", "CredAccountType", "Access"])

                        for item in result:
                                if item.access:
                                        access = "X"
                                else:
                                        access = ""
                                if item.credAccountType is None:
                                        credAccountType = ""
                                else:
                                        credAccountType = item.credAccountType
                                table.add_row([item.dbId, item.name, item.format.name, item.category.name, item.type, credAccountType, access])

                        printer.out("Target Format list for user \""+doArgs.account+"\" :")
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