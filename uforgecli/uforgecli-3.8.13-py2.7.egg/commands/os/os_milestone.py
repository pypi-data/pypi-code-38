__author__ = "UShareSoft"

from texttable import Texttable
from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from uforgecli.utils.uforgecli_utils import *
from uforgecli.utils.org_utils import org_get
from ussclicore.cmd import Cmd, CoreGlobal
from uforgecli.utils import org_utils
from ussclicore.utils import printer
from uforge.objects import uforge
from ussclicore.utils import generics_utils
from uforgecli.utils import uforgecli_utils
import datetime
import shlex

class Os_Milestone_Cmd(Cmd, CoreGlobal):
        """Manage roles entitlements"""

        cmd_name = "milestone"

        def __init__(self):
                super(Os_Milestone_Cmd, self).__init__()

        def arg_add(self):
                doParser = ArgumentParser(prog=self.cmd_name + " add", add_help=True, description="Add a milestone to a distribution.")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--darch', dest='darch', required=True, help="Operating system architecture (i386, x86_64).")
                mandatory.add_argument('--date', dest='date', required=True, help="The date of the milestone. The format is YYYY-MM-DD hh:mm:ss.")
                mandatory.add_argument('--dname', dest='dname', required=True, help="Operating system(s) name (for example CentOS, Debian etc) for which the current command should be executed.")
                mandatory.add_argument('--dversion', dest='dversion', required=True, help="Operating system version (13, 5.6, ...).")
                mandatory.add_argument('--name', dest='name', required=True, help="The name of the milestone.")
                optional.add_argument('--source', dest='source', required=False, help="The source of the milestone. It identifies the origin of this milestone.")
                optional.add_argument('--desc', dest='desc', required=False, help="The description of the milestone.")
                optional.add_argument('--org', dest='org', type=str, required=False, help="Organization which belongs the milestone. If not provided, default organization used.")

                return doParser

        def do_add(self, args):
                try:
                        # add arguments
                        doParser = self.arg_add()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        osList = self.api.Distributions.Getall()
                        osList = osList.distributions.distribution

                        org = org_get(api=self.api,name=doArgs.org)

                        os = None
                        for item in osList:
                                if item.name == doArgs.dname and item.arch == doArgs.darch and item.version == doArgs.dversion:
                                        os = item
                        if os is None:
                                printer.out("The distribution doesn't exist.", printer.ERROR)
                                return 0

                        newMilestone = milestone()
                        newMilestone.name = doArgs.name
                        newMilestone.date = datetime.datetime.strptime(doArgs.date, "%Y-%m-%d %H:%M:%S")

                        if doArgs.source is not None:
                                newMilestone.source = doArgs.source
                        if doArgs.desc is not None:
                                newMilestone.description = doArgs.desc

                        self.api.Distributions(os.dbId).Milestones.Create(body=newMilestone,Orgid=org.dbId)
                        printer.out("Milestone [" + newMilestone.name + "] has been added to [" + os.name + "]", printer.OK)
                        return 0
                except (ArgumentParserError, ValueError) as e:
                        printer.out("In Arguments: " + str(e), printer.ERROR)
                        self.help_add()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_add(self):
                doParser = self.arg_add()
                doParser.print_help()

        def arg_list(self):
                doParser = ArgumentParser(prog=self.cmd_name + " list", add_help=True, description="List all milestones from a distribution.")

                mandatory = doParser.add_argument_group("mandatory arguments")

                mandatory.add_argument('--darch', dest='darch', required=True, help="Operating system architecture (i386, x86_64).")
                mandatory.add_argument('--dname', dest='dname', required=True, help="Operating system(s) name (for example CentOS, Debian etc) for which the current command should be executed.")
                mandatory.add_argument('--dversion', dest='dversion', required=True, help="Operating system version (13, 5.6, ...).")
                return doParser

        def do_list(self, args):
                try:
                        # add arguments
                        doParser = self.arg_list()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        osList = self.api.Distributions.Getall()
                        osList = osList.distributions.distribution

                        os = None
                        for item in osList:
                                if item.name == doArgs.dname and item.arch == doArgs.darch and item.version == doArgs.dversion:
                                        os = item
                        if os is None:
                                printer.out("The distribution doesn't exist.", printer.ERROR)
                                return 0
                        milestoneList = self.api.Distributions(os.dbId).Milestones.Getall()
                        milestoneList = milestoneList.milestones.milestone

                        if len(milestoneList) > 0:
                                printer.out("List of milestone for [" + os.name + "] :")
                                table = Texttable(200)
                                table.set_cols_align(["c", "c", "c", "c", "c"])
                                table.header(["Id", "Milestone", "Source", "Description", "Date"])
                                for item in milestoneList:

                                        if item.date is None:
                                                date = "Unknown"
                                        else:
                                                date = item.date
                                        table.add_row([item.dbId, item.name, item.source, item.description, date])
                                print table.draw() + "\n"
                        else:
                                printer.out("There is no milestone for [" + os.name + "].")
                        return 0
                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_list()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_list(self):
                doParser = self.arg_list()
                doParser.print_help()

        def arg_modify(self):
                doParser = ArgumentParser(prog=self.cmd_name + " modify", add_help=True, description="Modify a milestone from an operating system.")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--darch', dest='darch', required=True, help="Operating system architecture (i386, x86_64).")
                mandatory.add_argument('--dname', dest='dname', required=True, help="Operating system(s) name (for example CentOS, Debian etc) for which the current command should be executed.")
                mandatory.add_argument('--dversion', dest='dversion', required=True, help="Operating system version (13, 5.6, ...).")
                mandatory.add_argument('--name', dest='name', required=True, help="The name of the milestone.")
                optional.add_argument('--source', dest='source', required=False, help="The source of the milestone. It identifies the origin of this milestone.")
                optional.add_argument('--desc', dest='desc', required=False, help="The description of the milestone.")
                optional.add_argument('--date', dest='date', required=False, help="The date of the milestone. The format is YYYY-MM-DD hh:mm:ss.")
                optional.add_argument('--org', dest='org', type=str, required=False, help="Organization where the milestone is. If not entered, default organization selected.")
                return doParser

        def do_modify(self, args):
                try:
                        doParser = self.arg_modify()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_get(api=self.api,name=doArgs.org)

                        allDistributions = self.api.Distributions.Getall()
                        distribution = None
                        for item in allDistributions.distributions.distribution:
                                if item.name == doArgs.dname and item.arch == doArgs.darch and item.version == doArgs.dversion:
                                        distribution = item
                        if distribution is None:
                                printer.out("The distribution associated doesn't exist.", printer.ERROR)
                                return 0
                        allMilestones = self.api.Distributions(distribution.dbId).Milestones.Getall()
                        Exist = False
                        newMilestone = milestone()
                        for item2 in allMilestones.milestones.milestone:
                                if item2.name == doArgs.name:
                                        Exist = True
                                        newMilestone.dbId = item2.dbId
                                        newMilestone.name = item2.name
                                        newMilestone.source = item2.source
                                        newMilestone.description = item2.description
                                        newMilestone.date = item2.date
                                        if doArgs.source is not None:
                                                newMilestone.source = doArgs.source
                                        if doArgs.desc is not None:
                                                newMilestone.description = doArgs.desc
                                        if doArgs.date is not None:
                                                newMilestone.date = datetime.datetime.strptime(doArgs.date, "%Y-%m-%d %H:%M:%S")
                                        break
                        if Exist:
                                self.api.Distributions(distribution.dbId).Milestones(newMilestone.dbId).Update(body=newMilestone, Orgid=org.dbId)
                                printer.out("Milestone [" + newMilestone.name + "] has been updated.", printer.OK)
                        return 0
                except (ArgumentParserError, ValueError) as e:
                        printer.out("In Arguments: " + str(e), printer.ERROR)
                        self.help_modify()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_modify(self):
                doParser = self.arg_modify()
                doParser.print_help()

        def arg_remove(self):
                doParser = ArgumentParser(prog=self.cmd_name + " remove", add_help=True, description="Remove a milestone from an operating system.")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--darch', dest='darch', required=True, help="Operating system architecture (i386, x86_64).")
                mandatory.add_argument('--dname', dest='dname', required=True, help="Operating system(s) name (for example CentOS, Debian etc) for which the current command should be executed.")
                mandatory.add_argument('--dversion', dest='dversion', required=True, help="Operating system version (13, 5.6, ...).")
                mandatory.add_argument('--name', dest='name', required=True, help="The name of the milestone.")
                optional.add_argument('--org', dest='org', type=str, required=False, help="Organization where the milestone is. If not provided, default organization used.")

                return doParser

        def do_remove(self, args):
                try:
                        doParser = self.arg_remove()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_get(api=self.api,name=doArgs.org)

                        allDistributions = self.api.Distributions.Getall()
                        distribution = None
                        for item in allDistributions.distributions.distribution:
                                if item.name == doArgs.dname and item.arch == doArgs.darch and item.version == doArgs.dversion:
                                        distribution = item
                        if distribution is None:
                                printer.out("The distribution associated doesn't exist.")
                                return 2
                        allMilestones = self.api.Distributions(distribution.dbId).Milestones.Getall()
                        for item2 in allMilestones.milestones.milestone:
                                if item2.name == doArgs.name:
                                        self.api.Distributions(distribution.dbId).Milestones(item2.dbId).Delete(Orgid=org.dbId)
                                        printer.out("Milestone [" + item2.name + "] has been deleted.", printer.OK)
                        return 0
                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_remove()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_remove(self):
                doParser = self.arg_remove()
                doParser.print_help()
