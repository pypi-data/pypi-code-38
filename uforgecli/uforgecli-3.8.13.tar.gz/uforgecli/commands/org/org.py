__author__="UShareSoft"

from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from ussclicore.cmd import Cmd, CoreGlobal
from texttable import Texttable
from uforgecli.utils.org_utils import org_get
from ussclicore.utils import generics_utils, printer
from ussclicore.utils.generics_utils import order_list_object_by
from uforgecli.utils.uforgecli_utils import *
from uforgecli.utils.org_utils import *
from org_user import Org_User_Cmd
from org_category import Org_Category_Cmd
from org_golden import Org_Golden_Cmd
from org_os import Org_Os_Cmd
from org_repo import Org_Repo_Cmd
from org_format import Org_Format_Cmd
from org_targetPlatform import Org_TargetPlatform_Cmd
from org_targetFormat import Org_TargetFormat_Cmd
from uforge.objects import uforge
from uforgecli.utils.compare_utils import compare
from uforgecli.utils import *
from hurry.filesize import size
import shlex


# Try on 10.1.2.114
# Where are the appliances

class Org_Cmd(Cmd, CoreGlobal):
        """Organization administration (list/info/update/delete etc)"""

        cmd_name = "org"

        def __init__(self):
                self.generate_sub_commands()
                super(Org_Cmd, self).__init__()

        def generate_sub_commands(self):
                if not hasattr(self, 'subCmds'):
                        self.subCmds = {}

                orgUser = Org_User_Cmd()
                self.subCmds[orgUser.cmd_name] = orgUser

                orgCategory = Org_Category_Cmd()
                self.subCmds[orgCategory.cmd_name] = orgCategory

                orgGolden = Org_Golden_Cmd()
                self.subCmds[orgGolden.cmd_name] = orgGolden

                orgOs = Org_Os_Cmd()
                self.subCmds[orgOs.cmd_name] = orgOs

                orgRepo = Org_Repo_Cmd()
                self.subCmds[orgRepo.cmd_name] = orgRepo

                orgFormat = Org_Format_Cmd()
                self.subCmds[orgFormat.cmd_name] = orgFormat

                orgTargetPlatform = Org_TargetPlatform_Cmd()
                self.subCmds[orgTargetPlatform.cmd_name] = orgTargetPlatform

                orgTargetFormat = Org_TargetFormat_Cmd()
                self.subCmds[orgTargetFormat.cmd_name] = orgTargetFormat

        def arg_list(self):
                doParser = ArgumentParser(add_help = True, description="List all the organizations")

                return doParser

        def do_list(self, args):
                try:
                        doParser = self.arg_list()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        allOrgs = self.api.Orgs.Getall()
                        allOrgs = order_list_object_by(allOrgs.orgs.org, "name")

                        printer.out("List of organizations :")

                        table = Texttable(200)
                        table.set_cols_align(["l", "l", "c", "c", "c"])
                        table.header(["Id", "Name", "Default", "Auto Activation", "Store"])

                        for item in allOrgs:
                                if item.defaultOrg:
                                        default = "X"
                                else:
                                        default = ""
                                if item.activateNewUsers:
                                        active = "X"
                                else:
                                        active = ""
                                if item.galleryUri is not None:
                                        gallery = "X"
                                else:
                                        gallery = ""
                                table.add_row([item.dbId, item.name, default, active, gallery])

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

        def arg_info(self):
                doParser = ArgumentParser(add_help = True, description="Get info on provided organization")

                optional = doParser.add_argument_group("optional arguments")

                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")
                return doParser

        def do_info(self, args):
                try:
                        doParser = self.arg_info()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)

                        orgInfo = self.api.Orgs(org.dbId).Get()

                        printer.out("Getting ["+orgInfo.name+"] :")

                        table = Texttable(200)
                        table.set_cols_align(["l", "l"])
                        table.add_row(["Name", orgInfo.name])
                        if orgInfo.defaultOrg:
                                defaultOrg = "Yes"
                        else:
                                defaultOrg = "No"
                        table.add_row(["Default Org", defaultOrg])
                        table.add_row(["Created", orgInfo.created.strftime("%Y-%m-%d %H:%M:%S")])
                        if orgInfo.activateNewUsers:
                                active = "Yes"
                        else:
                                active = "No"
                        table.add_row(["Auto Active New Accounts", active])
                        if orgInfo.galleryUri is not None:
                                galleryUri = "Yes"
                        else:
                                galleryUri = "No"
                        table.add_row(["Associated with a store", galleryUri])
                        print table.draw() + "\n"

                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_info()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_info(self):
                doParser = self.arg_info()
                doParser.print_help()
