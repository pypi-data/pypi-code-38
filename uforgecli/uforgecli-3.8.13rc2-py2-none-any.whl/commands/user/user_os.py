__author__ = "UShareSoft"

from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from ussclicore.cmd import Cmd, CoreGlobal
from texttable import Texttable
from uforgecli.utils.org_utils import org_get
from ussclicore.utils import generics_utils, printer
from uforgecli.utils.uforgecli_utils import *
from uforgecli.utils.compare_utils import *
from uforgecli.utils.texttable_utils import *
import pyxb
import shlex


class User_Os_Cmd(Cmd, CoreGlobal):
        """Administer users operating systems/distributions (list/enable/disable)"""

        cmd_name = "os"

        def __init__(self):
                super(User_Os_Cmd, self).__init__()

        def arg_list(self):
                doParser = ArgumentParser(add_help=True,description="List enabled operating systems for provided user")

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

                        printer.out("Getting distributions list for user \""+doArgs.account+"\"...")
                        distrosUser = self.api.Users(doArgs.account).Distros.Getall()
                        if distrosUser.total == 0:
                                printer.out("There is no distributions for the user \""+doArgs.account+"\".")
                                return 0
                        else:
                                distrosUser = generics_utils.order_list_object_by(distrosUser.distributions.distribution, "name")
                                printer.out("Distribution list for user \""+doArgs.account+"\" :")
                                table = init_texttable(["Id", "Distribution", "Version", "Architecture", "Access", "Visible", "Release Date"],
                                                       200,
                                                       ["c", "c", "c", "c", "c", "c", "c"],
                                                       ["t", "a", "t", "a", "a", "a", "a"])
                                for item in distrosUser:
                                        if item.active:
                                                active = "X"
                                        else:
                                                active = ""

                                        if item.visible:
                                                visible = "X"
                                        else:
                                                visible = ""

                                        if item.releaseDate is None:
                                                releaseDate = "Unknown"
                                        else:
                                                releaseDate = item.releaseDate
                                        table.add_row([item.dbId, item.name, item.version, item.arch, active, visible, releaseDate])
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
                doParser = ArgumentParser(add_help=True,description="Enable operating systems access for provided user")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--account', dest='account', type=str, required=True, help="User name of the account for which the current command should be executed")
                mandatory.add_argument('--name', dest='name', type=str, required=True, help="Operating system name (for example CentOS, Debian etc) for which the current command should be executed. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")

                optional.add_argument('--arch', dest='arch', type=str, required=False, help="Operating system architecture (i386 | x86_64) for which the current command should be executed. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--version', dest='version', type=str, required=False, help="Operating system version (13, 5.6, ...) for which the current command should be executed. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--org', dest='org', type=str, required=False, help="Organization where the operating system is.")
                return doParser

        def do_enable(self, args):
                try:
                        doParser = self.arg_enable()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_get(api=self.api,name=doArgs.org)

                        printer.out("Getting distributions list from ["+org.name+"]...")
                        distrosOrg = self.api.Orgs(org.dbId).Distributions.Getall(Name=None, Version=None, Arch=None, Info=None, body=None)
                        distrosOrg = distrosOrg.distributions.distribution

                        if distrosOrg is None or len(distrosOrg) == 0:
                                printer.out("[" + org.name + "] does not have any available operating systems.")
                                return 0

                        distrosOrg = compare(distrosOrg, doArgs.name, "name")
                        if doArgs.version is not None:
                                distrosOrg = compare(distrosOrg, doArgs.version, "version")
                        if doArgs.arch is not None:
                                distrosOrg = compare(distrosOrg, doArgs.arch, "arch")

                        printer.out("Updating distributions list for user \""+doArgs.account+"\" :")

                        distribs = distributions()
                        distribs.distributions = pyxb.BIND()

                        for item in distrosOrg:
                                newDistro = distribution()
                                newDistro = item
                                newDistro.active = True
                                newDistro.visible = True
                                distribs.distributions.append(newDistro)

                        returnList = self.api.Users(doArgs.account).Distros.Update(Org=org.name,body=distribs)
                        printer.out("List for user \""+doArgs.account+"\" enabled :", printer.OK)
                        returnList = returnList.distributions.distribution

                        table = init_texttable(["Distribution", "Version", "Architecture", "Access", "Visible", "Release Date"],
                                               200,
                                               ["c", "c", "c", "c", "c", "c"],
                                               ["a", "t", "a", "a", "a", "a"])
                        for item in returnList:
                                if item.active:
                                        active = "X"
                                else:
                                        active = ""

                                if item.visible:
                                        visible = "X"
                                else:
                                        visible = ""

                                if item.releaseDate is None:
                                        releaseDate = "Unknown"
                                else:
                                        releaseDate = item.releaseDate
                                table.add_row([item.name, item.version, item.arch, active, visible, releaseDate])
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
                doParser = ArgumentParser(add_help=True,description="Disable operating systems access for provided user")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--account', dest='account', type=str, required=True,help="User name of the account for which the current command should be executed")
                mandatory.add_argument('--name', dest='name', type=str, required=True,help="Operating system name (for example CentOS, Debian etc) for which the current command should be executed. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")

                optional.add_argument('--arch', dest='arch', type=str, required=False,help="Operating system architecture (i386 | x86_64) for which the current command should be executed. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--version', dest='version', type=str, required=False,help="Operating system version (13, 5.6, ...) for which the current command should be executed. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--org', dest='org', type=str, required=False,help="Organization where the operating system is.")
                return doParser

        def do_disable(self, args):
                try:
                        doParser = self.arg_disable()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_get(api=self.api,name=doArgs.org)
                        printer.out("Getting distributions list for user \""+doArgs.account+"\".")

                        distrosUser = self.api.Users(doArgs.account).Distros.Getall()
                        distrosUser = distrosUser.distributions.distribution

                        distrosUser = compare(distrosUser, doArgs.name, "name")
                        if doArgs.version is not None:
                                distrosUser = compare(distrosUser, doArgs.version, "version")
                        if doArgs.arch is not None:
                                distrosUser = compare(distrosUser, doArgs.arch, "arch")

                        distribs = distributions()
                        distribs.distributions = pyxb.BIND()
                        for item in distrosUser:
                                newDistro = distribution()
                                newDistro = item
                                newDistro.active = False
                                distribs.distributions.append(newDistro)

                        printer.out("Updating distributions list for user \""+doArgs.account+"\" :")
                        returnList = self.api.Users(doArgs.account).Distros.Update(Org=org.name,body=distribs)
                        printer.out("List for user \""+doArgs.account+"\" updated :", printer.OK)

                        table = init_texttable(["Distribution", "Version", "Architecture", "Access", "Visible", "Release Date"],
                                               200,
                                               ["c", "c", "c", "c", "c", "c"],
                                               ["a", "t", "a", "a", "a", "a"])
                        for item in returnList.distributions.distribution:
                                if item.active:
                                        active = "X"
                                else:
                                        active = ""

                                if item.visible:
                                        visible = "X"
                                else:
                                        visible = ""

                                if item.releaseDate is None:
                                        releaseDate = "Unknown"
                                else:
                                        releaseDate = item.releaseDate
                                table.add_row([item.name, item.version, item.arch, active, visible, releaseDate])
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