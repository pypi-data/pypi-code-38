__author__ = "UShareSoft"

from texttable import Texttable
from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from uforgecli.utils.uforgecli_utils import *
from ussclicore.cmd import Cmd, CoreGlobal
from uforgecli.utils import org_utils
from ussclicore.utils.generics_utils import order_list_object_by
from ussclicore.utils import printer
from org_repo_os import Org_Repo_Os_Cmd
from org_repo_refresh import Org_Repo_Refresh_Cmd
from requests.exceptions import ReadTimeout
from uforge.objects import uforge
from ussclicore.utils import generics_utils
from uforgecli.utils import uforgecli_utils
import pyxb
from pyxb.exceptions_ import SimpleFacetValueError
import datetime
import shlex

class Org_Repo_Cmd(Cmd, CoreGlobal):
        """Repository operation (list|create|delete|update)"""

        cmd_name = "repo"

        def __init__(self):
                self.generate_sub_commands()
                super(Org_Repo_Cmd, self).__init__()

        def generate_sub_commands(self):
                if not hasattr(self, 'subCmds'):
                        self.subCmds = {}

                orgRepoOs = Org_Repo_Os_Cmd()
                self.subCmds[orgRepoOs.cmd_name] = orgRepoOs

                orgRepoRefresh = Org_Repo_Refresh_Cmd()
                self.subCmds[orgRepoRefresh.cmd_name] = orgRepoRefresh

        def arg_list(self):
                doParser = ArgumentParser(add_help = True, description="List all the repositories for the provided organization")

                optional = doParser.add_argument_group("optional arguments")

                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")
                optional.add_argument('--sortField', dest='sort', type=str, required=False, help="Sort the repository list by a field between Name, ID, Url and Type")

                return doParser

        def do_list(self, args):
                try:
                        doParser = self.arg_list()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)
                        allRepo = self.api.Orgs(org.dbId).Repositories.Getall()

                        if allRepo is None:
                                printer.out("No repositories found in [" + org.name + "].")
                                return 0

                        if doArgs.sort is not None:
                                if doArgs.sort.lower() == "name":
                                        printer.out("Repository list ordered by [name] :")
                                        allRepo = order_list_object_by(allRepo.repositories.repository, "name")
                                elif doArgs.sort.lower() == "id":
                                        printer.out("Repository list ordered by [id] :")
                                        allRepo = sorted(allRepo.repositories.repository, key=lambda x: getattr(x, "dbId"), reverse=False)
                                elif doArgs.sort.lower() == "url":
                                        printer.out("Repository list ordered by [url] :")
                                        allRepo = order_list_object_by(allRepo.repositories.repository, "url")
                                elif doArgs.sort.lower() == "type":
                                        printer.out("Repository list ordered by [type] :")
                                        allRepo = order_list_object_by(allRepo.repositories.repository, "packagingType")
                                else:
                                        printer.out("Sorting parameter filled don't exist.", printer.WARNING)
                                        printer.out("Repository list :")
                                        allRepo = sorted(allRepo.repositories.repository, key=lambda x: getattr(x, "dbId"), reverse=False)
                        else:
                                printer.out("Repository list :")
                                allRepo = sorted(allRepo.repositories.repository, key=lambda x: getattr(x, "dbId"), reverse=False)

                        table = Texttable(200)
                        table.set_cols_align(["c", "c", "l", "l", "c"])
                        table.set_cols_width([5,5,30,80,8])
                        table.header(["Id", "Core Repo", "Name", "URL", "Type"])

                        for item in allRepo:
                                if item.coreRepository:
                                        coreRepository = "X"
                                else:
                                        coreRepository = ""
                                table.add_row([item.dbId, coreRepository, item.name, item.url, item.packagingType])

                        print table.draw() + "\n"

                        printer.out("Found " + str(len(allRepo)) + " repositories.")

                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_list()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_list(self):
                doParser = self.arg_list()
                doParser.print_help()

        def arg_create(self):
                doParser = ArgumentParser(add_help = True, description="Create a repository in the organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--name', dest='name', type=str, required=True, help="Repository name.")
                mandatory.add_argument('--repoUrl', dest='repoUrl', type=str, required=True, help="Url of the repository to create in the organization.")
                mandatory.add_argument('--type', dest='type', type=str, required=True, help="Type of the repository to create in the organization ('RPM' or 'DEB').")
                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")
                optional.add_argument('-o', '--coreRepository', dest='coreRepository', action="store_true", required=False, help="flag for repositories that are mandatory for a distribution to function properly.")
                optional.add_argument('--officiallySupported', dest='officiallySupported', action="store_true", required=False, help="[DEPRECATED] use --coreRepository instead.")

                return doParser

        def do_create(self, args):
                try:
                        doParser = self.arg_create()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)
                        allRepo = self.api.Orgs(org.dbId).Repositories.Getall()
                        allRepo = allRepo.repositories.repository

                        for item in allRepo:
                                if doArgs.repoUrl == item.url:
                                        printer.out("The repository with URL [" + item.url + "] already exist in [" + org.name + "].", printer.ERROR)
                                        return 0

                        newRepository = repository()
                        newRepository.url = doArgs.repoUrl
                        newRepository.packagingType = doArgs.type
                        newRepository.name = doArgs.name
                        newRepository.coreRepository = doArgs.coreRepository
                        # Keep compatibility with officiallySupported option that is now deprecated
                        if doArgs.officiallySupported:
                                newRepository.coreRepository = True

                        result = self.api.Orgs(org.dbId).Repositories.Create(body=newRepository)
                        printer.out("Successfully created repository with URL [" + doArgs.repoUrl + "] in [" + org.name + "].", printer.OK)

                        table = Texttable(200)
                        table.header(["Id", "Core Repo", "Name", "URL", "Type"])
                        if result.coreRepository:
                                coreRepository = "X"
                        else:
                                coreRepository = ""
                        table.add_row([result.dbId, coreRepository, result.name, result.url, result.packagingType])
                        print table.draw() + "\n"
                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_create()
                except SimpleFacetValueError as e:
                        printer.out("The type name "+e.value+" is not allowed. You can choose RPM or DEB.", printer.ERROR)
                        return 2
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_create(self):
                doParser = self.arg_create()
                doParser.print_help()

        def arg_delete(self):
                doParser = ArgumentParser(add_help = True, description="Delete a repository in the organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--ids', dest='ids', nargs='+', required=True, help="One or more repositories to delete (repository Ids provided) in the organization.  Ids separated by space (e.g. 1 2 3)")
                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")

                return doParser

        def do_delete(self, args):
                removing_id = -1
                try:
                        doParser = self.arg_delete()
                        doArgs = doParser.parse_args(shlex.split(args))

                        # if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)
                        not_handled = []
                        not_handled.extend(doArgs.ids)

                        for item in doArgs.ids:
                                removing_id = item
                                not_handled.remove(item)
                                self.api.Orgs(org.dbId).Repositories(item).Delete()
                                printer.out("Repository with ID [" + str(item) + "] deleted.", printer.OK)

                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_delete()
                except ReadTimeout as e:
                        if removing_id != -1:
                                printer.out("Request timed out. \n"
                                            + "Delete process [" + str(removing_id) + "] of the repository is still "
                                            + "running. If in a few minutes the repository has not been deleted, "
                                            + "please contact your system administrator.", printer.INFO)
                                if len(not_handled) > 0:
                                        printer.out("The repositories with the following ID: " + str(not_handled)
                                                    + " have not been deleted. Please try again later.", printer.INFO)
                        else:
                                return handle_uforge_exception(e)
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_delete(self):
                doParser = self.arg_delete()
                doParser.print_help()

        def arg_update(self):
                doParser = ArgumentParser(add_help = True, description="Update a repository in the organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--id', dest='id', type=int, required=True, help="Id of the repository to update in the organization.")
                optional.add_argument('--repoUrl', dest='repoUrl', type=str, required=False, help="Url of the repository to update in the organization.")
                optional.add_argument('--type', dest='type', type=str, required=False, help="Type of the repository to update in the organization.")
                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")

                return doParser

        def do_update(self, args):
                try:
                        doParser = self.arg_update()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)
                        allRepo = self.api.Orgs(org.dbId).Repositories.Getall()
                        allRepo = allRepo.repositories.repository

                        if doArgs.repoUrl is None and doArgs.type is None:
                                printer.out("No change has been specified.")
                                return 0

                        for item in allRepo:
                                if doArgs.repoUrl == item.url:
                                        printer.out("The URL is already used by repository with ID [" + str(item.dbId) + "]", printer.ERROR)
                                        return 0
                                if doArgs.id == item.dbId:
                                        newRepository = repository()
                                        newRepository.url = item.url
                                        newRepository.packagingType = item.packagingType
                                        newRepository.name = item.name
                                        newRepository.coreRepository = item.coreRepository
                                        newRepository.distributionsUriList = item.distributionsUriList
                                        if doArgs.repoUrl is not None:
                                                newRepository.url = doArgs.repoUrl
                                        if doArgs.type is not None:
                                                newRepository.packagingType = doArgs.type
                                        result = self.api.Orgs(org.dbId).Repositories(item.dbId).Update(body=newRepository)
                                        printer.out("Updated repository with ID [" + str(doArgs.id) + "].", printer.OK)
                                        return 0

                        printer.out("The repository specified doesn't exist.", printer.ERROR)
                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_update()
                except SimpleFacetValueError as e:
                        printer.out("The type name "+e.value+" is not allowed. You can choose RPM or DEB.", printer.ERROR)
                        return 2
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_update(self):
                doParser = self.arg_update()
                doParser.print_help()
