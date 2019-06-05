__author__ = "UShareSoft"

from texttable import Texttable
from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from uforgecli.utils.uforgecli_utils import *
from ussclicore.cmd import Cmd, CoreGlobal
from uforgecli.utils import org_utils
from ussclicore.utils.generics_utils import order_list_object_by
from ussclicore.utils import printer
from uforgecli.utils.compare_utils import compare
from uforge.objects import uforge
from ussclicore.utils import generics_utils
from uforgecli.utils import uforgecli_utils
from uforgecli.utils.texttable_utils import *
import pyxb
import datetime
import shlex

class Org_Repo_Os_Cmd(Cmd, CoreGlobal):
        """Repository OS operation (list|attach|detach)"""

        cmd_name = "os"

        def __init__(self):
                super(Org_Repo_Os_Cmd, self).__init__()

        def arg_list(self):
                doParser = ArgumentParser(add_help = True, description="List distributions belonging to a repository in the organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--repoId', dest='repoId', type=str, required=True, help="Id of the repository.")
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
                        allDist = self.api.Orgs(org.dbId).Repositories(doArgs.repoId).Distributions.Getall()
                        allDist = order_list_object_by(allDist.distributions.distribution, "name")

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

                        printer.out("Found "+str(len(allDist))+" in repository with ID [" + doArgs.repoId + "] and in organization ["+org.name+"].", printer.OK)
                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_list()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_list(self):
                doParser = self.arg_list()
                doParser.print_help()

        def arg_attach(self):
                doParser = ArgumentParser(add_help = True, description="Attach a distribution to a repository in the organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--arch', dest='arch', type=str, required=True, help="Operating system architecture (i386, x86_64).")
                mandatory.add_argument('--name', dest='name', type=str, required=True, help="Operating system(s) name (for example CentOS, Debian etc) for which the current command should be executed.")
                mandatory.add_argument('--repoIds', dest='repoIds', nargs='+', required=True, help="Ids of the repository to update.")
                mandatory.add_argument('--version', dest='version', type=str, required=True, help="Operating system version (13, 5.6, ...)")
                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")

                return doParser

        def do_attach(self, args):
                try:
                        doParser = self.arg_attach()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)
                        allDist = self.api.Orgs(org.dbId).Distributions.Getall()
                        allDist = allDist.distributions.distribution

                        dist = None
                        for item in allDist:
                                if item.arch == doArgs.arch and item.version == doArgs.version and item.name == doArgs.name:
                                        dist = item

                        if dist is None:
                                printer.out("No distribution found with the currents arguments.")
                                return 0

                        allRepo = self.api.Orgs(org.dbId).Repositories.Getall()
                        allRepo = allRepo.repositories.repository

                        for repo in allRepo:
                                for itemList in doArgs.repoIds:
                                        if repo.dbId == int(itemList):
                                                newRepository = repository()
                                                newRepository.url = repo.url
                                                newRepository.packagingType = repo.packagingType
                                                newRepository.name = repo.name
                                                newRepository.coreRepository = repo.coreRepository
                                                newRepository.distributionsUriList = repo.distributionsUriList
                                                newRepository.distributionsUriList.append(dist.uri)
                                                result = self.api.Orgs(org.dbId).Repositories(repo.dbId).Update(body=newRepository)
                                                printer.out("Distribution(s) attached to repository ID [" + str(repo.dbId) + "] in [" + org.name + "].", printer.OK)

                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_attach()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_attach(self):
                doParser = self.arg_attach()
                doParser.print_help()

        def arg_detach(self):
                doParser = ArgumentParser(add_help = True, description="Detach a distribution to a repository in the organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--arch', dest='arch', type=str, required=True, help="Operating system architecture (i386, x86_64).")
                mandatory.add_argument('--name', dest='name', type=str, required=True, help="Operating system(s) name (for example CentOS, Debian etc) for which the current command should be executed.")
                mandatory.add_argument('--repoIds', dest='repoIds', nargs='+', required=True, help="Ids of the repository to update.")
                mandatory.add_argument('--version', dest='version', type=str, required=True, help="Operating system version (13, 5.6, ...)")
                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")

                return doParser

        def do_detach(self, args):
                try:
                        doParser = self.arg_detach()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)
                        allDist = self.api.Orgs(org.dbId).Distributions.Getall()
                        allDist = allDist.distributions.distribution

                        dist = None
                        for item in allDist:
                                if item.arch == doArgs.arch and item.version == doArgs.version and item.name == doArgs.name:
                                        dist = item

                        if dist is None:
                                printer.out("No distribution found with the currents arguments.")
                                return 0

                        allRepo = self.api.Orgs(org.dbId).Repositories.Getall()
                        allRepo = allRepo.repositories.repository

                        for repo in allRepo:
                                for itemList in doArgs.repoIds:
                                        if repo.dbId == int(itemList):
                                                newRepository = repository()
                                                newRepository.url = repo.url
                                                newRepository.packagingType = repo.packagingType
                                                newRepository.name = repo.name
                                                newRepository.coreRepository = repo.coreRepository
                                                newRepository.distributionsUriList = repo.distributionsUriList
                                                newRepository.distributionsUriList.uri.remove(dist.uri)
                                                result = self.api.Orgs(org.dbId).Repositories(repo.dbId).Update(body=newRepository)
                                                printer.out("Distribution(s) detached from repository ID [" + str(repo.dbId) + "] in [" + org.name + "].", printer.OK)

                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_detach()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_detach(self):
                doParser = self.arg_detach()
                doParser.print_help()