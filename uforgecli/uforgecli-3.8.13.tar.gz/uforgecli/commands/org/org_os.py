__author__ = "UShareSoft"

from texttable import Texttable
from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from uforgecli.utils.uforgecli_utils import *
from ussclicore.cmd import Cmd, CoreGlobal
from uforgecli.utils import org_utils
from ussclicore.utils.generics_utils import order_list_object_by
from ussclicore.utils import printer
from uforge.objects import uforge
from ussclicore.utils import generics_utils
from uforgecli.utils import uforgecli_utils
from uforgecli.utils.texttable_utils import *
import pyxb
from uforgecli.utils.compare_utils import compare
import datetime
import shlex

class Org_Os_Cmd(Cmd, CoreGlobal):
        """OS operation (list|add|enable|disable)"""

        cmd_name = "os"

        def __init__(self):
                super(Org_Os_Cmd, self).__init__()

        def arg_list(self):
                doParser = ArgumentParser(add_help = True, description="List all the operating systems (enabled and disabled) for the provided organization")

                optional = doParser.add_argument_group("optional arguments")

                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")

                return doParser

        def do_list(self, args):
                try:
                        doParser = self.arg_list()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)
                        allDist = self.api.Orgs(org.dbId).Distributions.Getall()
                        if allDist is None:
                                printer.out("No distributions found in [" + org.name + "].")
                                return 0
                        allDist = generics_utils.order_list_object_by(allDist.distributions.distribution, "name")

                        table = init_texttable(["Id", "Distribution", "Version", "Architecture", "Access", "Visible", "Default", "Release Date"],
                                               200,
                                               ["l", "l", "l", "l", "l", "l", "l", "l"],
                                               ["t", "a", "t", "a", "a", "a", "a", "a"])

                        for item in allDist:
                                if item.active:
                                        access = "X"
                                else:
                                        access = ""
                                if item.visible:
                                        visible = "X"
                                else:
                                        visible = ""
                                if item.preselected:
                                        default = "X"
                                else:
                                        default = ""
                                if item.releaseDate is None:
                                        date = "Unknown"
                                else:
                                        date = item.releaseDate.strftime("%Y-%m-%d %H:%M:%S")
                                table.add_row([item.dbId, item.name, item.version, item.arch, access, visible, default, date])

                        print table.draw() + "\n"

                        printer.out("Found "+str(len(allDist))+" distributions in organization ["+org.name+"].")
                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_list()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_list(self):
                doParser = self.arg_list()
                doParser.print_help()

        def arg_add(self):
                doParser = ArgumentParser(add_help = True, description="Add an operating system for the provided organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--arch', dest='arch', type=str, required=True, help="Operating system architecture (i386, x86_64).")
                mandatory.add_argument('--name', dest='name', type=str, required=True, help="Operating system(s) name (for example CentOS, Debian etc) for which the current command should be executed.")
                mandatory.add_argument('--version', dest='version', type=str, required=True, help="Operating system version (13, 5.6, ...)")
                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")

                return doParser

        def do_add(self, args):
                try:
                        doParser = self.arg_add()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)

                        newDist = distribution()
                        newDist.active = True
                        newDist.preselected = False
                        newDist.arch = doArgs.arch
                        newDist.name = doArgs.name
                        newDist.version = doArgs.version

                        result = self.api.Orgs(org.dbId).Distributions.Add(body=newDist)
                        printer.out("Distribution [" + result.name + "] version " + result.version + " has been created", printer.OK)
                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_add()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_add(self):
                doParser = self.arg_add()
                doParser.print_help()

        def arg_enable(self):
                doParser = ArgumentParser(add_help = True, description="Enable one or more operating systems for the provided organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--name', dest='name', nargs='+', required=True, help="Operating system(s) name (for example CentOS, Debian etc) for which the current command should be executed. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--arch', dest='arch', nargs='+', required=False, help="Operating system architecture (i386, x86_64). You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--version', dest='version', nargs='+', required=False, help="Operating system version (13, 5.6, ...). You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")

                return doParser

        def do_enable(self, args):
                try:
                        doParser = self.arg_enable()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)
                        allDist = self.api.Orgs(org.dbId).Distributions.Getall()

                        if allDist is None:
                                printer.out("No distribution found with the currents arguments.")
                                return 0

                        allDist = allDist.distributions.distribution

                        allDist = compare(allDist, doArgs.name, "name")
                        if doArgs.version is not None:
                                allDist = compare(allDist, doArgs.version, "version")
                        if doArgs.arch is not None:
                                allDist = compare(allDist, doArgs.arch, "arch")

                        newAllDists = distributions()
                        newAllDists.distributions = pyxb.BIND()

                        for item in allDist:
                                newDist = distribution()
                                newDist = item
                                newDist.active = True
                                newDist.visible = True
                                newAllDists.distributions.append(newDist)

                        result = self.api.Orgs(org.dbId).Distributions.Update(body=newAllDists)
                        if result is None:
                                printer.out("No distribution was updated. It could be that the distributions are already enabled.")
                                return 0

                        table = init_texttable(["Distribution", "Version", "Architecture", "Access", "Visible", "Default", "Release Date"],
                                               200,
                                               ["l", "l", "l", "l", "l", "l", "l"],
                                               ["a", "t", "a", "a", "a", "a", "a"])
                        printer.out("Distribution(s) has been enabled.", printer.OK)
                        for dist in result.distributions.distribution:
                                if dist.active:
                                        access = "X"
                                else:
                                        access = ""
                                if dist.visible:
                                        visible = "X"
                                else:
                                        visible = ""
                                if dist.preselected:
                                        default = "X"
                                else:
                                        default = ""
                                if dist.releaseDate is None:
                                        date = "Unknown"
                                else:
                                        date = dist.releaseDate.strftime("%Y-%m-%d %H:%M:%S")
                                table.add_row([dist.name, dist.version, dist.arch, access, visible, default, date])

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
                doParser = ArgumentParser(add_help = True, description="Disable one or more operating systems for the provided organization.  Disabling will remove this as a 'default' operating system")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--name', dest='name', nargs='+', required=True, help="Operating system(s) name (for example CentOS, Debian etc) for which the current command should be executed. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--arch', dest='arch', nargs='+', required=False, help="Operating system architecture (i386, x86_64). You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--version', dest='version', nargs='+', required=False, help="Operating system version (13, 5.6, ...). You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")

                return doParser

        def do_disable(self, args):
                try:
                        doParser = self.arg_disable()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)
                        allDist = self.api.Orgs(org.dbId).Distributions.Getall()

                        if allDist is None:
                                printer.out("No distribution found with the currents arguments.")
                                return 0

                        allDist = allDist.distributions.distribution

                        allDist = compare(allDist, doArgs.name, "name")
                        if doArgs.version is not None:
                                allDist = compare(allDist, doArgs.version, "version")
                        if doArgs.arch is not None:
                                allDist = compare(allDist, doArgs.arch, "arch")

                        newAllDists = distributions()
                        newAllDists.distributions = pyxb.BIND()

                        for item in allDist:
                                newDist = distribution()
                                newDist = item
                                newDist.active = False
                                newDist.visible = False
                                newAllDists.distributions.append(newDist)

                        result = self.api.Orgs(org.dbId).Distributions.Update(body=newAllDists)
                        if result is None:
                                printer.out("No distribution was updated. It could be that the distributions are already disabled.")
                                return 0

                        table = init_texttable(["Distribution", "Version", "Architecture", "Access", "Visible", "Default", "Release Date"],
                                               200,
                                               ["l", "l", "l", "l", "l", "l", "l"],
                                               ["a", "t", "a", "a", "a", "a", "a"])
                        printer.out("Distribution(s) has been disabled.", printer.OK)
                        for dist in result.distributions.distribution:
                                if dist.active:
                                        access = "X"
                                else:
                                        access = ""
                                if dist.visible:
                                        visible = "X"
                                else:
                                        visible = ""
                                if dist.preselected:
                                        default = "X"
                                else:
                                        default = ""
                                if dist.releaseDate is None:
                                        date = "Unknown"
                                else:
                                        date = dist.releaseDate.strftime("%Y-%m-%d %H:%M:%S")
                                table.add_row([dist.name, dist.version, dist.arch, access, visible, default, date])

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

