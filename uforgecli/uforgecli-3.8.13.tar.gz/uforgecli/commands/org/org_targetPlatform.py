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
from uforgecli.utils.compare_utils import compare
import pyxb
import datetime
import shlex

class Org_TargetPlatform_Cmd(Cmd, CoreGlobal):
        """TargetPlatform operation (list|create|update|addTargetFormat|removeTargetFormat|enable|disable|delete)"""

        cmd_name = "targetplatform"

        def __init__(self):
                super(Org_TargetPlatform_Cmd, self).__init__()

        def arg_list(self):
                doParser = ArgumentParser(add_help = True, description="List all target platforms for the provided organization")

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
                        if org is None:
                                printer.out("There is no organization matching ["+doArgs.org+"].", printer.OK)
                                return 0

                        printer.out("Getting target platform list for ["+org.name+"] . . .")
                        allTargetPlatforms = self.api.Orgs(org.dbId).Targetplatforms.Getall()
                        allTargetPlatforms = order_list_object_by(allTargetPlatforms.targetPlatforms.targetPlatform, "name")

                        if len(allTargetPlatforms) == 0:
                                printer.out("There is no target platforms in ["+org.name+"].", printer.OK)
                                return 0

                        table = Texttable(200)
                        table.set_cols_align(["c", "l", "l", "c"])
                        table.header(["Id", "Name", "Type", "Access"])

                        for item in allTargetPlatforms:
                                if item.access:
                                        access = "X"
                                else:
                                        access = ""
                                table.add_row([item.dbId, item.name, item.type, access])

                        print table.draw() + "\n"
                        printer.out("Found "+str(len(allTargetPlatforms))+" target platforms.", printer.OK)
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
                doParser = ArgumentParser(add_help=True, description="Create a target platform in the organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--name', dest='name', type=str, required=True, help="Name of the target platform to create in the organization.")
                mandatory.add_argument('--type', dest='type', type=str, required=True, help="Type of the target platform to create in the organization (aws, azure, google, cloudcom, openstack, vclouddirector, vsphere).")
                optional.add_argument('--accountInfos', dest='accountInfos', type=str, required=False, help="Account information of the target platform (example: cloud provider's URL).")
                optional.add_argument('--file', dest='file', required=False, help="The logo file.")
                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")

                return doParser

        def do_create(self, args):
                try:
                        doParser = self.arg_create()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)
                        if org is None:
                                printer.out("There is no organization matching ["+doArgs.org+"].", printer.OK)
                                return 0

                        newTargetPlatform = targetPlatform()
                        newTargetPlatform.name = doArgs.name
                        newTargetPlatform.type = doArgs.type
                        if doArgs.accountInfos is not None:
                                newTargetPlatform.accountInfos = doArgs.accountInfos

                        result = self.api.Orgs(org.dbId).Targetplatforms.Create(body=newTargetPlatform)
                        if doArgs.file is not None and result is not None:
                                fileName = os.path.basename(doArgs.file)
                                file = open(doArgs.file, "r")
                                self.api.Orgs(org.dbId).Targetplatforms(result.dbId).Logo(Logoid=result.logo.dbId, Filename=fileName).Upload(body=file)
                        printer.out("Target Platform ["+newTargetPlatform.name+"] has successfully been created.", printer.OK)

                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_create()
                except pyxb.SimpleFacetValueError as e:
                        printer.out("Unknown type ["+str(e.value)+"] for target platform." , printer.ERROR)
                        values = None
                        for value in e.type.values():
                                if values is None:
                                        values = value
                                else:
                                        values = values + ", " + value
                        printer.out("Please change for one of these values: " + values, printer.ERROR)
                        return 2
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_create(self):
                doParser = self.arg_create()
                doParser.print_help()

        def arg_update(self):
                doParser = ArgumentParser(add_help=True, description="Update a target platform in the organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--id', dest='id', type=str, required=True, help="Id of the target platform to update in the organization.")
                mandatory.add_argument('--name', dest='name', type=str, required=True, help="(New) Name of the target platform to update in the organization.")
                optional.add_argument('--type', dest='type', type=str, required=False, help="(New Type of the target platform to update in the organization (aws, azure, google, cloudcom, openstack, vclouddirector, vsphere).")
                optional.add_argument('--accountInfos', dest='accountInfos', type=str, required=False, help="(New) Account information of the target platform (example: cloud provider's URL).")
                optional.add_argument('--file', dest='file', required=False, help="The logo file.")
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
                        if org is None:
                                printer.out("There is no organization matching ["+doArgs.org+"].", printer.OK)
                                return 0

                        printer.out("Getting target platform with id ["+doArgs.id+"] for ["+org.name+"] . . .")
                        targetPlatformToUpdate = self.api.Orgs(org.dbId).Targetplatforms(doArgs.id).Get()
                        if targetPlatformToUpdate is None:
                                printer.out("targetFormat with id "+ doArgs.id +" does not exist", printer.ERROR)
                                return 2
                        else:
                                targetPlatformToUpdate.name = doArgs.name
                                if doArgs.type is not None:
                                        targetPlatformToUpdate.type = doArgs.type
                                if doArgs.accountInfos is not None:
                                        targetPlatformToUpdate.accountInfos = doArgs.accountInfos
                                result = self.api.Orgs(org.dbId).Targetplatforms(doArgs.id).Update(body=targetPlatformToUpdate)
                                if doArgs.file is not None and result is not None:
                                        fileName = os.path.basename(doArgs.file)
                                        file = open(doArgs.file, "r")
                                        self.api.Orgs(org.dbId).Targetplatforms(result.dbId).Logo(Logoid=result.logo.dbId, Filename=fileName).Upload(body=file)
                                printer.out("Target Platform ["+targetPlatformToUpdate.name+"] has successfully been updated.", printer.OK)

                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_update()
                except pyxb.SimpleFacetValueError as e:
                        printer.out("Unknown type ["+str(e.value)+"] for target platform." , printer.ERROR)
                        values = None
                        for value in e.type.values():
                                if values is None:
                                        values = value
                                else:
                                        values = values + ", " + value
                        printer.out("Please change for one of these values: " + values, printer.ERROR)
                        return 2
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_update(self):
                doParser = self.arg_update()
                doParser.print_help()

        def arg_listTargetFormat(self):
                doParser = ArgumentParser(add_help=True, description="List all target format in the provided target platform in the organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--id', dest='id', type=str, required=True, help="Id of the target platform you want to list target formats.")
                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")

                return doParser

        def do_listTargetFormat(self, args):
                try:
                        doParser = self.arg_listTargetFormat()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)
                        if org is None:
                                printer.out("There is no organization matching ["+doArgs.org+"].", printer.OK)
                                return 0

                        printer.out("Getting target platform with id ["+doArgs.id+"] for ["+org.name+"] . . .")
                        targetPlatform = self.api.Orgs(org.dbId).Targetplatforms(doArgs.id).Get()
                        if targetPlatform is None:
                                printer.out("TargetPlatform with id "+ doArgs.id +" does not exist", printer.ERROR)
                                return 2
                        else:
                                printer.out("Getting target format list for target platform ["+targetPlatform.name+"] . . .")
                                allTargetFormats = self.api.Orgs(org.dbId).Targetplatforms(targetPlatform.dbId).Targetformats.Getallformats()
                                allTargetFormats = order_list_object_by(allTargetFormats.targetFormats.targetFormat, "name")

                                if len(allTargetFormats) == 0:
                                        printer.out("There is no target formats in target platform ["+targetPlatform.name+"].", printer.OK)
                                        return 0

                        printer.out("Found "+str(len(allTargetFormats))+" target formats in target platform ["+targetPlatform.name+"].", printer.OK)
                        table = Texttable(200)
                        table.set_cols_align(["c", "l", "l", "l", "l", "l", "c"])
                        table.header(["Id", "Name", "Format", "Category", "Type", "CredAccountType", "Access"])

                        for item in allTargetFormats:
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
                        self.help_listTargetFormat()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_listTargetFormat(self):
                doParser = self.arg_listTargetFormat()
                doParser.print_help()

        def arg_addTargetFormat(self):
                doParser = ArgumentParser(add_help=True, description="Add one or more target formats to a target platform in the organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--id', dest='id', type=str, required=True, help="Id of the target platform where adding target formats.")
                mandatory.add_argument('--targetFormats', dest='targetFormats', nargs='+', required=True, help="target format(s) to put in the target platform.")
                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")

                return doParser

        def do_addTargetFormat(self, args):
                try:
                        doParser = self.arg_addTargetFormat()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)
                        if org is None:
                                printer.out("There is no organization matching ["+doArgs.org+"].", printer.OK)
                                return 0

                        printer.out("Getting target platform with id ["+doArgs.id+"] for ["+org.name+"] . . .")
                        targetPlatform = self.api.Orgs(org.dbId).Targetplatforms(doArgs.id).Get()
                        if targetPlatform is None:
                                printer.out("TargetPlatform with id "+ doArgs.id +" does not exist", printer.ERROR)
                                return 2
                        else:
                                printer.out("Getting target format list for ["+org.name+"] . . .")
                                allTargetFormats = self.api.Orgs(org.dbId).Targetformats.Getall()
                                allTargetFormats = allTargetFormats.targetFormats.targetFormat

                                if len(allTargetFormats) == 0:
                                        printer.out("There is no target formats in ["+org.name+"].", printer.WARNING)
                                        return 0

                                allTargetFormats = compare(allTargetFormats, doArgs.targetFormats, "name")

                                if len(allTargetFormats) == 0:
                                        listName = ""
                                        for tfname in doArgs.targetFormats:
                                                listName = listName + tfname + " "
                                        printer.out("There is no target formats matching ["+listName+"].", printer.ERROR)
                                        return 2

                                for item in allTargetFormats:
                                        targetFormatToAdd = targetFormat()
                                        targetFormatToAdd.name = item.name
                                        result = self.api.Orgs(org.dbId).Targetplatforms(targetPlatform.dbId).Targetformats.Addformat(body=targetFormatToAdd)
                                        printer.out("Target Format ["+targetFormatToAdd.name+"] has successfully been added to Target platform ["+targetPlatform.name+"].", printer.OK)

                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_addTargetFormat()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_addTargetFormat(self):
                doParser = self.arg_addTargetFormat()
                doParser.print_help()

        def arg_removeTargetFormat(self):
                doParser = ArgumentParser(add_help=True, description="Remove one or more target formats from a target platform in the organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--id', dest='id', type=str, required=True, help="Id of the target platform where removing target formats.")
                mandatory.add_argument('--targetFormats', dest='targetFormats', nargs='+', required=True, help="target format(s) to remove from the target platform.")
                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")

                return doParser

        def do_removeTargetFormat(self, args):
                try:
                        doParser = self.arg_removeTargetFormat()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)
                        if org is None:
                                printer.out("There is no organization matching ["+doArgs.org+"].", printer.OK)
                                return 0

                        printer.out("Getting target platform with id ["+doArgs.id+"] for ["+org.name+"] . . .")
                        targetPlatform = self.api.Orgs(org.dbId).Targetplatforms(doArgs.id).Get()
                        if targetPlatform is None:
                                printer.out("TargetPlatform with id "+ doArgs.id +" does not exist", printer.ERROR)
                                return 2
                        else:
                                printer.out("Getting target format list for ["+org.name+"] . . .")
                                allTargetFormats = self.api.Orgs(org.dbId).Targetformats.Getall()
                                allTargetFormats = allTargetFormats.targetFormats.targetFormat

                                if len(allTargetFormats) == 0:
                                        printer.out("There is no target formats in ["+org.name+"].", printer.WARNING)
                                        return 0

                                allTargetFormats = compare(allTargetFormats, doArgs.targetFormats, "name")

                                if len(allTargetFormats) == 0:
                                        listName = ""
                                        for tfname in doArgs.targetFormats:
                                                listName = listName + tfname + " "
                                        printer.out("There is no target formats matching ["+listName+"].", printer.ERROR)
                                        return 2

                                for item in allTargetFormats:
                                        result = self.api.Orgs(org.dbId).Targetplatforms(doArgs.id).Targetformats(item.dbId).Removeformat()
                                        printer.out("Target Format ["+item.name+"] has successfully been removed from Target platform ["+targetPlatform.name+"].", printer.OK)

                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_removeTargetFormat()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_removeTargetFormat(self):
                doParser = self.arg_removeTargetFormat()
                doParser.print_help()

        def arg_enable(self):
                doParser = ArgumentParser(add_help = True, description="Enable one or more target platforms for the provided organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--targetPlatforms', dest='targetPlatforms', nargs='+', required=True, help="TargetPlatform(s) for which the current command should be executed. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
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
                        if org is None:
                                printer.out("There is no organization matching ["+doArgs.org+"].", printer.OK)
                                return 0

                        printer.out("Getting target platform list for ["+org.name+"] . . .")
                        allTargetPlatforms = self.api.Orgs(org.dbId).Targetplatforms.Getall()
                        allTargetPlatforms = allTargetPlatforms.targetPlatforms.targetPlatform

                        if len(allTargetPlatforms) == 0:
                                printer.out("There is no target platforms in ["+org.name+"].", printer.WARNING)
                                return 0

                        all_targetplatforms = targetPlatforms()
                        all_targetplatforms.targetPlatforms = pyxb.BIND()

                        allTargetPlatforms = compare(allTargetPlatforms, doArgs.targetPlatforms, "name")

                        if len(allTargetPlatforms) == 0:
                                listName = ""
                                for tpname in doArgs.targetPlatforms:
                                        listName = listName + tpname + " "
                                printer.out("There is no target platforms matching ["+listName+"].", printer.ERROR)
                                return 2

                        for item in allTargetPlatforms:
                                targetPlatformToEnable = targetPlatform()
                                targetPlatformToEnable = item
                                targetPlatformToEnable.active = True
                                targetPlatformToEnable.access = True
                                printer.out("Enabling ["+item.name+"].")
                                all_targetplatforms.targetPlatforms.append(targetPlatformToEnable)

                        result = self.api.Orgs(org.dbId).Targetplatforms.Updateaccess(body=all_targetplatforms)

                        if result is None or len(result.targetPlatforms.targetPlatform) == 0:
                                printer.out("The target platforms(s) selected are already enabled", printer.WARNING)
                                return 0
                        sentenceReturn = "Target Platform(s)"
                        for tp in result.targetPlatforms.targetPlatform:
                                sentenceReturn = sentenceReturn + " " + tp.name + " "
                        printer.out(sentenceReturn + "has/have been enabled.", printer.OK)

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
                doParser = ArgumentParser(add_help = True, description="Disable one or more target platforms for the provided organization.")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--targetPlatforms', dest='targetPlatforms', nargs='+', required=True, help="Target Platform(s) for which the current command should be executed. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
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
                        if org is None:
                                printer.out("There is no organization matching ["+doArgs.org+"].", printer.OK)
                                return 0

                        printer.out("Getting target platform list for ["+org.name+"] . . .")
                        allTargetPlatforms = self.api.Orgs(org.dbId).Targetplatforms.Getall()
                        allTargetPlatforms = allTargetPlatforms.targetPlatforms.targetPlatform

                        if len(allTargetPlatforms) == 0:
                                printer.out("There is no target platforms in ["+org.name+"].", printer.WARNING)
                                return 0

                        all_targetplatforms = targetPlatforms()
                        all_targetplatforms.targetPlatforms = pyxb.BIND()

                        allTargetPlatforms = compare(allTargetPlatforms, doArgs.targetPlatforms, "name")

                        if len(allTargetPlatforms) == 0:
                                listName = ""
                                for tpname in doArgs.targetPlatforms:
                                        listName = listName + tpname + " "
                                printer.out("There is no target platforms matching ["+listName+"].", printer.ERROR)
                                return 2

                        for item in allTargetPlatforms:
                                targetPlatformToDisable = targetPlatform()
                                targetPlatformToDisable = item
                                targetPlatformToDisable.active = False
                                targetPlatformToDisable.access = False
                                printer.out("Disabling ["+item.name+"].")
                                all_targetplatforms.targetPlatforms.append(targetPlatformToDisable)

                        result = self.api.Orgs(org.dbId).Targetplatforms.Updateaccess(body=all_targetplatforms)

                        if result is None or len(result.targetPlatforms.targetPlatform) == 0:
                                printer.out("The target platforms(s) selected are already disabled", printer.WARNING)
                                return 0
                        sentenceReturn = "Target Platform(s)"
                        for tp in result.targetPlatforms.targetPlatform:
                                sentenceReturn = sentenceReturn + " " + tp.name + " "
                        printer.out(sentenceReturn + "has/have been disabled.", printer.OK)

                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_disable()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_disable(self):
                doParser = self.arg_disable()
                doParser.print_help()

        def arg_delete(self):
                doParser = ArgumentParser(add_help=True, description="Delete a target platform in the organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--id', dest='id', type=str, required=True, help="Id of the target platform to delete in the organization.")
                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")

                return doParser

        def do_delete(self, args):
                try:
                        doParser = self.arg_delete()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)
                        if org is None:
                                printer.out("There is no organization matching ["+doArgs.org+"].", printer.OK)
                                return 0

                        printer.out("Getting target platform with id ["+doArgs.id+"] for ["+org.name+"] . . .")
                        targetPlatform = self.api.Orgs(org.dbId).Targetplatforms(doArgs.id).Get()
                        if targetPlatform is None:
                                printer.out("targetPlatform with id "+ doArgs.id +" does not exist", printer.ERROR)
                                return 2
                        else:
                                result = self.api.Orgs(org.dbId).Targetplatforms(doArgs.id).Delete()
                                printer.out("Target Platform ["+targetPlatform.name+"] has successfully been deleted.", printer.OK)

                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_delete()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_delete(self):
                doParser = self.arg_delete()
                doParser.print_help()