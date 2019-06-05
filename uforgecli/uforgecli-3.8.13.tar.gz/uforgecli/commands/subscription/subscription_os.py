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


class Subscription_Os(Cmd, CoreGlobal):
        """Manage subscription profile os"""

        cmd_name = "os"

        def __init__(self):
                super(Subscription_Os, self).__init__()

        def arg_add(self):
                doParser = ArgumentParser(prog=self.cmd_name + " add", add_help=True, description="Add an OS to a subscription profile")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--name', dest='name', required=True, help="The name of the subscription profile")
                mandatory.add_argument('--os', dest='os', nargs='+', required=True, help="Operating system name (for example CentOS, Debian etc) for which the current command should be executed. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--version', dest='version', nargs='+', required=False, help="Operating system version (13, 5.6, ...) for which the current command should be executed. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--arch', dest='arch', nargs='+', required=False, help="Operating system architecture (i386 | x86_64) for which the current command should be executed. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--org', dest='org', required=False, help="The organization name. If no organization is provided, then the default organization is used.")
                optional.add_argument('--allusers', dest='allusers', action="store_true", required=False, help="if set, all existing active users of that subscription profile benefit from the operating system addition.")

                return doParser

        def do_add(self, args):
                try:
                        doParser = self.arg_add()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        printer.out("Getting subscription profile with name [" + doArgs.name + "]...")
                        org = org_utils.org_get(self.api, doArgs.org)
                        subscriptions = self.api.Orgs(org.dbId).Subscriptions().Getall(Search=None)
                        osList = self.api.Orgs(org.dbId).Distributions.Getall()
                        osList = osList.distributions.distribution
                        if osList == None:
                                printer.out("The organization as no OS available")

                        if doArgs.os is not None:
                                osList = compare(osList, doArgs.os, "name")
                        if doArgs.version is not None:
                                osList = compare(osList, doArgs.version, "version")
                        if doArgs.arch is not None:
                                osList = compare(osList, doArgs.arch, "arch")

                        subProfileSelected = None
                        exist = False
                        for subProfile in subscriptions.subscriptionProfiles.subscriptionProfile:
                                if subProfile.name == doArgs.name:
                                        subProfileSelected = subProfile
                                        exist = True
                                        all_distros = distributions()
                                        all_distros.distributions = pyxb.BIND()

                                        for nr in osList:
                                                all_distros.distributions.append(nr)

                        if not exist:
                                printer.out("Subscription profile requested don't exist in [" + org.name + "]")
                                return 0
                        self.api.Orgs(org.dbId).Subscriptions(subProfileSelected.dbId).Distros.Update(Allusers=doArgs.allusers, body=all_distros)
                        printer.out("Some OS added for subscription profile [" + doArgs.name + "]...", printer.OK)
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
                doParser = ArgumentParser(prog=self.cmd_name + " remove", add_help=True, description="Remove one or several OS from a subscription profile")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--name', dest='name', required=True, help="The name of the subscription profile")
                mandatory.add_argument('--os', dest='os', nargs='+', required=True, help="Operating system name (for example CentOS, Debian etc) for which the current command should be executed. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--version', dest='version', nargs='+', required=False, help="Operating system version (13, 5.6, ...) for which the current command should be executed. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--arch', dest='arch', nargs='+', required=False, help="Operating system architecture (i386 | x86_64) for which the current command should be executed. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--org', dest='org', required=False, help="The organization name. If no organization is provided, then the default organization is used.")
                optional.add_argument('--allusers', dest='allusers', action="store_true", required=False, help="if set, all existing active users of that subscription profile benefit from the operating system deletion.")

                return doParser

        def do_remove(self, args):
                try:
                        doParser = self.arg_remove()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        printer.out("Getting subscription profile with name [" + doArgs.name + "]...")
                        org = org_utils.org_get(self.api, doArgs.org)
                        subscriptions = self.api.Orgs(org.dbId).Subscriptions().Getall(Search=None)
                        osList = self.api.Orgs(org.dbId).Distributions.Getall()
                        osList = osList.distributions.distribution
                        if osList == None:
                                printer.out("The organization as no OS available")

                        if doArgs.os is not None:
                                osList = compare(osList, doArgs.os, "name")
                        if doArgs.version is not None:
                                osList = compare(osList, doArgs.version, "version")
                        if doArgs.arch is not None:
                                osList = compare(osList, doArgs.arch, "arch")

                        if len(osList) == 0:
                                printer.out("There is no distribution matching the request.")
                                return 0

                        subProfileSelected = None
                        exist = False
                        for subProfile in subscriptions.subscriptionProfiles.subscriptionProfile:
                                if subProfile.name == doArgs.name:
                                        subProfileSelected = subProfile
                                        exist = True
                                        all_distros = distributions()
                                        all_distros.distributions = pyxb.BIND()

                                        for distribItem in subProfile.distributions.distribution:
                                                for nr in osList:
                                                        if distribItem.name == nr.name and distribItem.version == nr.version and distribItem.arch == nr.arch:
                                                                distro = distribution()
                                                                distro = nr
                                                                distro.active = False
                                                                all_distros.distributions.append(distro)
                                                        
                        if not exist:
                                printer.out("Subscription profile requested don't exist in [" + org.name + "]")
                                return 0
                        self.api.Orgs(org.dbId).Subscriptions(subProfileSelected.dbId).Distros.Update(Allusers=doArgs.allusers, body=all_distros)
                        printer.out("Some OS removed for subscription profile [" + doArgs.name + "]...", printer.OK)
                        return 0

                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_remove()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_remove(self):
                doParser = self.arg_remove()
                doParser.print_help()