__author__ = "UShareSoft"

from texttable import Texttable
from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from ussclicore.cmd import Cmd, CoreGlobal
from uforgecli.utils import org_utils
from uforgecli.utils.compare_utils import compare
from ussclicore.utils import printer
from ussclicore.utils import generics_utils
from uforgecli.utils.uforgecli_utils import *
from uforge.objects import uforge
from uforgecli.utils import uforgecli_utils
import pyxb
import shlex


class Subscription_TargetPlatform(Cmd, CoreGlobal):
        """Manage subscription profile target platforms"""

        cmd_name = "targetplatform"

        def __init__(self):
                super(Subscription_TargetPlatform, self).__init__()

        def arg_add(self):
                doParser = ArgumentParser(prog=self.cmd_name + " add", add_help=True, description="Add target platforms to a subscription profile")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--name', dest='name', required=True, help="the name of the subscription profile")
                mandatory.add_argument('--targetPlatforms', dest='targetPlatforms', nargs='+', required=True, help="targetPlatform(s) for which the current command should be executed. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--org', dest='org', required=False, help="the organization name. If no organization is provided, then the default organization is used.")
                optional.add_argument('--allusers', dest='allusers', action="store_true", required=False, help="if set, all existing active users of that subscription profile benefit from the target platform addition.")

                return doParser

        def do_add(self, args):
                try:
                        # add arguments
                        doParser = self.arg_add()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        printer.out("Getting subscription profile with name [" + doArgs.name + "]...")
                        org = org_utils.org_get(self.api, doArgs.org)
                        if org is None:
                                printer.out("There is no organization matching ["+doArgs.org+"].", printer.OK)
                                return 0

                        subscriptions = self.api.Orgs(org.dbId).Subscriptions().Getall(Search=None)
                        orgTargetPlatforms = self.api.Orgs(org.dbId).Targetplatforms.Getall()
                        if orgTargetPlatforms is None:
                                printer.out("The organization as no target platform available.")
                                return 0

                        exist = False
                        subProfileSelected = None
                        for item in subscriptions.subscriptionProfiles.subscriptionProfile:
                                if item.name == doArgs.name:
                                        exist = True
                                        subProfileSelected = item
                                        all_targetPlatforms = targetPlatforms()
                                        all_targetPlatforms.targetPlatforms = pyxb.BIND()

                                        newTargetPlatforms = compare(orgTargetPlatforms.targetPlatforms.targetPlatform, doArgs.targetPlatforms, "name")

                                        if len(newTargetPlatforms) == 0:
                                                listName = ""
                                                for tpname in doArgs.targetPlatforms:
                                                        listName = listName + tpname + " "
                                                printer.out("There is no target platforms matching ["+listName+"].")
                                                return 0

                                        for nr in newTargetPlatforms:
                                                all_targetPlatforms.targetPlatforms.append(nr)
                                                printer.out("Added target platform " + nr.name + " for subscription.")

                                        self.api.Orgs(org.dbId).Subscriptions(subProfileSelected.dbId).Targetplatforms.Update(Allusers=doArgs.allusers, body=all_targetPlatforms)
                                        printer.out("Some target platforms added for subscription profile [" + doArgs.name + "]...", printer.OK)
                        if not exist:
                                printer.out("Subscription profile requested don't exist in [" + org.name + "]")
                        return 0

                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_add()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_add(self):
                doParser = self.arg_add()
                doParser.print_help()

        def arg_remove(self):
                doParser = ArgumentParser(prog=self.cmd_name + " remove", add_help=True, description="Remove one or several target platforms from a subscription profile")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--name', dest='name', required=True, help="the name of the subscription profile")
                mandatory.add_argument('--targetPlatforms', dest='targetPlatforms', nargs='+', required=True, help="targetPlatform(s) for which the current command should be executed. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--org', dest='org', required=False, help="the organization name. If no organization is provided, then the default organization is used.")
                optional.add_argument('--allusers', dest='allusers', action="store_true", required=False, help="if set, all existing active users of that subscription profile benefit from the target platform deletion.")

                return doParser

        def do_remove(self, args):
                try:
                        # add arguments
                        doParser = self.arg_remove()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        printer.out("Getting subscription profile with name [" + doArgs.name + "]...")
                        org = org_utils.org_get(self.api, doArgs.org)
                        if org is None:
                                printer.out("There is no organization matching ["+doArgs.org+"].", printer.OK)
                                return 0

                        subscriptions = self.api.Orgs(org.dbId).Subscriptions().Getall(Search=None)

                        exist = False
                        subProfileSelected = None
                        for item in subscriptions.subscriptionProfiles.subscriptionProfile:
                                if item.name == doArgs.name:
                                        exist = True
                                        subProfileSelected = item
                                        all_targetPlatforms = targetPlatforms()
                                        all_targetPlatforms.targetPlatforms = pyxb.BIND()

                                        newTargetPlatforms = compare(item.targetPlatforms.targetPlatform, doArgs.targetPlatforms, "name")

                                        if len(newTargetPlatforms) == 0:
                                                listName = ""
                                                for tpname in doArgs.targetPlatforms:
                                                        listName = listName + tpname + " "
                                                printer.out("There is no target platforms matching ["+listName+"].")
                                                return 0

                                        for targetPlatformItem in item.targetPlatforms.targetPlatform:
                                                for deleteList in newTargetPlatforms:
                                                        if targetPlatformItem.name == deleteList.name:
                                                                already_targetPlatform = targetPlatform()
                                                                already_targetPlatform.access = targetPlatformItem.access
                                                                already_targetPlatform.active = False
                                                                already_targetPlatform.name = targetPlatformItem.name
                                                                already_targetPlatform.uri = targetPlatformItem.uri
                                                                all_targetPlatforms.targetPlatforms.append(already_targetPlatform)
                                                                printer.out("Removed target platform " + targetPlatformItem.name + " for subscription.")

                                        # call UForge API
                                        self.api.Orgs(org.dbId).Subscriptions(subProfileSelected.dbId).Targetplatforms.Update(Allusers=doArgs.allusers, body=all_targetPlatforms)
                                        printer.out("Some target platforms removed from subscription profile [" + doArgs.name + "]...", printer.OK)

                        if not exist:
                                printer.out("Subscription profile requested don't exist in [" + org.name + "]")
                        return 0

                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_remove()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_remove(self):
                doParser = self.arg_remove()
                doParser.print_help()