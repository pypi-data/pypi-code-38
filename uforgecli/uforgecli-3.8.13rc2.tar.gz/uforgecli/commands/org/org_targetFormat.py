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
import os.path

categoryImageFormat = "IMAGEFORMAT"
fieldImageFormat = "image format"
fieldType = "type"
fieldCredAccountType = "credAccountType"

class Org_TargetFormat_Cmd(Cmd, CoreGlobal):
        """TargetFormat operation (list|create|update|addTargetPlatform|removeTargetPlatform|enable|disable|delete)"""

        cmd_name = "targetformat"

        def __init__(self):
                super(Org_TargetFormat_Cmd, self).__init__()

        def arg_list(self):
                doParser = ArgumentParser(add_help = True, description="List all target formats for the provided organization")

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

                        printer.out("Getting target format list for ["+org.name+"] . . .")
                        allTargetFormats = self.api.Orgs(org.dbId).Targetformats.Getall()
                        allTargetFormats = order_list_object_by(allTargetFormats.targetFormats.targetFormat, "name")

                        if len(allTargetFormats) == 0:
                                printer.out("There is no target formats in ["+org.name+"].", printer.OK)
                                return 0

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
                        printer.out("Found "+str(len(allTargetFormats))+" target formats.", printer.OK)
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
                doParser = ArgumentParser(add_help=True, description="Create a target format in the organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--name', dest='name', type=str, required=True, help="Name of the target format to create in the organization.")
                mandatory.add_argument('--format', dest='format', type=str, required=True, help="Name of the image format used for the target format to create in the organization.")
                mandatory.add_argument('--category', dest='category', type=str, required=True, help="Name of the target format category for the target format to create in the organization.")
                mandatory.add_argument('--type', dest='type', type=str, required=True, help="Type of the target format to create in the organization (cloud, virtual, container, physical).")
                optional.add_argument('--credAccountType', dest='credAccountType', type=str, required=False, help="Credential account type of the target format to create in the organization (aws, azure, google, cloudcom, openstack, vclouddirector, vsphere).")
                optional.add_argument('--credInfos', dest='credInfos', type=str, required=False, help="Credential information of the target format to create in the organization.")
                optional.add_argument('--imageInfos', dest='imageInfos', type=str, required=False, help="Image information of the target format to create in the organization.")
                optional.add_argument('--publishInfos', dest='publishInfos', type=str, required=False, help="Publish information of the target format to create in the organization.")
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

                        newTargetFormat = targetFormat()
                        newTargetFormat.name = doArgs.name
                        field = fieldImageFormat
                        format = imageFormat()
                        format.name = doArgs.format
                        newTargetFormat.format = format
                        targetFormatCategory = category()
                        targetFormatCategory.name = doArgs.category
                        targetFormatCategory.type = categoryImageFormat
                        newTargetFormat.category = targetFormatCategory
                        field = fieldType
                        newTargetFormat.type = doArgs.type
                        if doArgs.credAccountType is not None:
                                field = fieldCredAccountType
                                newTargetFormat.credAccountType = doArgs.credAccountType
                        if doArgs.credInfos is not None:
                                newTargetFormat.credInfos = doArgs.credInfos
                        if doArgs.imageInfos is not None:
                                newTargetFormat.imageInfos = doArgs.imageInfos
                        if doArgs.publishInfos is not None:
                                newTargetFormat.publishInfos = doArgs.publishInfos

                        result = self.api.Orgs(org.dbId).Targetformats.Create(body=newTargetFormat)
                        if doArgs.file is not None and result is not None:
                                fileName = os.path.basename(doArgs.file)
                                file = open(doArgs.file, "r")
                                self.api.Orgs(org.dbId).Targetformats(result.dbId).Logo(Logoid=result.logo.dbId, Filename=fileName).Upload(body=file)

                        printer.out("Target Format ["+newTargetFormat.name+"] has successfully been created.", printer.OK)

                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_create()
                except pyxb.SimpleFacetValueError as e:
                        printer.out("Unknown " + field + " ["+str(e.value)+"] for target format." , printer.ERROR)
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
                doParser = ArgumentParser(add_help=True, description="Update a target format in the organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--id', dest='id', type=str, required=True, help="Id of the target format to update in the organization.")
                mandatory.add_argument('--name', dest='name', type=str, required=True, help="(New) Name of the target format to update in the organization.")
                optional.add_argument('--format', dest='format', type=str, required=False, help="(New) Name of the image format used for the target format to update in the organization.")
                optional.add_argument('--category', dest='category', type=str, required=False, help="(New) Name of the target format category for the target format to update in the organization.")
                optional.add_argument('--type', dest='type', type=str, required=False, help="(New) Type of the target format to update in the organization (cloud, virtual, container, physical).")
                optional.add_argument('--credAccountType', dest='credAccountType', type=str, required=False, help="(New) Credential account type of the target format to update in the organization (aws, azure, google, cloudcom, openstack, vclouddirector, vsphere).")
                optional.add_argument('--credInfos', dest='credInfos', type=str, required=False, help="(New) Credential information of the target format to update in the organization.")
                optional.add_argument('--imageInfos', dest='imageInfos', type=str, required=False, help="(New) Image information of the target format to update in the organization.")
                optional.add_argument('--publishInfos', dest='publishInfos', type=str, required=False, help="(New) Publish information of the target format to update in the organization.")
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

                        printer.out("Getting target format with id ["+doArgs.id+"] for ["+org.name+"] . . .")
                        targetFormat = self.api.Orgs(org.dbId).Targetformats(doArgs.id).Get()
                        if targetFormat is None:
                                printer.out("targetFormat with id "+ doArgs.id +" does not exist", printer.ERROR)
                                return 2
                        else:
                                targetFormat.name = doArgs.name
                                if doArgs.format is not None:
                                        field = fieldImageFormat
                                        format = imageFormat()
                                        format.name = doArgs.format
                                        targetFormat.format = format
                                if doArgs.category is not None:
                                        targetFormatCategory = category()
                                        targetFormatCategory.name = doArgs.category
                                        targetFormatCategory.type = categoryImageFormat
                                        targetFormat.category = targetFormatCategory
                                if doArgs.type is not None:
                                        field = fieldType
                                        targetFormat.type = doArgs.type
                                if doArgs.credAccountType is not None:
                                        field = fieldCredAccountType
                                        targetFormat.credAccountType = doArgs.credAccountType
                                if doArgs.credInfos is not None:
                                        targetFormat.credInfos = doArgs.credInfos
                                if doArgs.imageInfos is not None:
                                        targetFormat.imageInfos = doArgs.imageInfos
                                if doArgs.publishInfos is not None:
                                        targetFormat.publishInfos = doArgs.publishInfos

                        result = self.api.Orgs(org.dbId).Targetformats(doArgs.id).Update(body=targetFormat)
                        if doArgs.file is not None and result is not None:
                                fileName = os.path.basename(doArgs.file)
                                file = open(doArgs.file, "r")
                                self.api.Orgs(org.dbId).Targetformats(result.dbId).Logo(Logoid=result.logo.dbId, Filename=fileName).Upload(body=file)

                        printer.out("Target Format ["+targetFormat.name+"] has successfully been updated.", printer.OK)

                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_update()
                except pyxb.SimpleFacetValueError as e:
                        printer.out("Unknown " + field + " ["+str(e.value)+"] for target format." , printer.ERROR)
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

        def arg_listTargetPlatform(self):
                doParser = ArgumentParser(add_help=True, description="List all target platform in the provided target format in the organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--id', dest='id', type=str, required=True, help="Id of the target format you want to list target platforms.")
                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")

                return doParser

        def do_listTargetPlatform(self, args):
                try:
                        doParser = self.arg_listTargetPlatform()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)
                        if org is None:
                                printer.out("There is no organization matching ["+doArgs.org+"].", printer.OK)
                                return 0

                        printer.out("Getting target format with id ["+doArgs.id+"] for ["+org.name+"] . . .")
                        targetFormat = self.api.Orgs(org.dbId).Targetformats(doArgs.id).Get()
                        if targetFormat is None:
                                printer.out("targetFormat with id "+ doArgs.id +" does not exist", printer.ERROR)
                                return 2
                        else:
                                printer.out("Getting target platform list for target format ["+targetFormat.name+"] . . .")
                                allTargetPlatforms = self.api.Orgs(org.dbId).Targetformats(targetFormat.dbId).Targetplatforms.Getalltargetplatforms()
                                allTargetPlatforms = order_list_object_by(allTargetPlatforms.targetPlatforms.targetPlatform, "name")

                                if len(allTargetPlatforms) == 0:
                                        printer.out("There is no target platforms in target format ["+targetFormat.name+"].", printer.OK)
                                        return 0

                        printer.out("Found "+str(len(allTargetPlatforms))+" target platforms in target format ["+targetFormat.name+"].", printer.OK)
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
                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_listTargetPlatform()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_listTargetPlatform(self):
                doParser = self.arg_listTargetPlatform()
                doParser.print_help()

        def arg_addTargetPlatform(self):
                doParser = ArgumentParser(add_help=True, description="Add one or more target platforms to a target format in the organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--id', dest='id', type=str, required=True, help="Id of the target format to add to target platforms.")
                mandatory.add_argument('--targetPlatforms', dest='targetPlatforms', nargs='+', required=True, help="target platform(s) in which put the target format.")
                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")

                return doParser

        def do_addTargetPlatform(self, args):
                try:
                        doParser = self.arg_addTargetPlatform()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)
                        if org is None:
                                printer.out("There is no organization matching ["+doArgs.org+"].", printer.OK)
                                return 0

                        printer.out("Getting target format with id ["+doArgs.id+"] for ["+org.name+"] . . .")
                        targetFormat = self.api.Orgs(org.dbId).Targetformats(doArgs.id).Get()
                        if targetFormat is None:
                                printer.out("targetFormat with id "+ doArgs.id +" does not exist", printer.ERROR)
                                return 2
                        else:
                                printer.out("Getting target platform list for ["+org.name+"] . . .")
                                allTargetPlatforms = self.api.Orgs(org.dbId).Targetplatforms.Getall()
                                allTargetPlatforms = allTargetPlatforms.targetPlatforms.targetPlatform

                                if len(allTargetPlatforms) == 0:
                                        printer.out("There is no target platforms in ["+org.name+"].", printer.WARNING)
                                        return 0

                                allTargetPlatforms = compare(allTargetPlatforms, doArgs.targetPlatforms, "name")

                                if len(allTargetPlatforms) == 0:
                                        listName = ""
                                        for tpname in doArgs.targetPlatforms:
                                                listName = listName + tpname + " "
                                        printer.out("There is no target platforms matching ["+listName+"].", printer.ERROR)
                                        return 2

                                for item in allTargetPlatforms:
                                        targetPlatformToAdd = targetPlatform()
                                        targetPlatformToAdd.name = item.name
                                        result = self.api.Orgs(org.dbId).Targetformats(targetFormat.dbId).Targetplatforms.Addtargetplatform(body=targetPlatformToAdd)
                                        printer.out("Target Platform ["+targetPlatformToAdd.name+"] has successfully been added to Target format ["+targetFormat.name+"].", printer.OK)

                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_addTargetPlatform()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_addTargetPlatform(self):
                doParser = self.arg_addTargetPlatform()
                doParser.print_help()

        def arg_removeTargetPlatform(self):
                doParser = ArgumentParser(add_help=True, description="Remove one or more target platforms from a target format in the organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--id', dest='id', type=str, required=True, help="Id of the target format to remove to target platforms.")
                mandatory.add_argument('--targetPlatforms', dest='targetPlatforms', nargs='+', required=True, help="target platform(s) in which remove the target format.")
                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")

                return doParser

        def do_removeTargetPlatform(self, args):
                try:
                        doParser = self.arg_removeTargetPlatform()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)
                        if org is None:
                                printer.out("There is no organization matching ["+doArgs.org+"].", printer.OK)
                                return 0

                        printer.out("Getting target format with id ["+doArgs.id+"] for ["+org.name+"] . . .")
                        targetFormat = self.api.Orgs(org.dbId).Targetformats(doArgs.id).Get()
                        if targetFormat is None:
                                printer.out("Format with id "+ doArgs.id +" does not exist", printer.ERROR)
                                return 2
                        else:
                                printer.out("Getting target platform list for ["+org.name+"] . . .")
                                allTargetPlatforms = self.api.Orgs(org.dbId).Targetplatforms.Getall()
                                allTargetPlatforms = allTargetPlatforms.targetPlatforms.targetPlatform

                                if len(allTargetPlatforms) == 0:
                                        printer.out("There is no target platforms in ["+org.name+"].", printer.WARNING)
                                        return 0

                                allTargetPlatforms = compare(allTargetPlatforms, doArgs.targetPlatforms, "name")

                                if len(allTargetPlatforms) == 0:
                                        listName = ""
                                        for tpname in doArgs.targetPlatforms:
                                                listName = listName + tpname + " "
                                        printer.out("There is no target platforms matching ["+listName+"].", printer.ERROR)
                                        return 2

                                for item in allTargetPlatforms:
                                        result = self.api.Orgs(org.dbId).Targetformats(doArgs.id).Targetplatforms(item.dbId).Removetargetplatform()
                                        printer.out("Target platform ["+item.name+"] has successfully been removed from Target format ["+targetFormat.name+"].", printer.OK)

                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_removeTargetPlatform()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_removeTargetPlatform(self):
                doParser = self.arg_removeTargetPlatform()
                doParser.print_help()

        def arg_enable(self):
                doParser = ArgumentParser(add_help = True, description="Enable one or more target formats for the provided organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--targetFormats', dest='targetFormats', nargs='+', required=True, help="TargetFormat(s) for which the current command should be executed. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
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

                        printer.out("Getting target format list for ["+org.name+"] . . .")
                        allTargetFormats = self.api.Orgs(org.dbId).Targetformats.Getall()
                        allTargetFormats = allTargetFormats.targetFormats.targetFormat

                        if len(allTargetFormats) == 0:
                                printer.out("There is no target formats in ["+org.name+"].", printer.WARNING)
                                return 0

                        all_targetformats = targetFormats()
                        all_targetformats.targetFormats = pyxb.BIND()

                        allTargetFormats = compare(allTargetFormats, doArgs.targetFormats, "name")

                        if len(allTargetFormats) == 0:
                                listName = ""
                                for tfname in doArgs.targetFormats:
                                        listName = listName + tfname + " "
                                printer.out("There is no target formats matching ["+listName+"].", printer.ERROR)
                                return 2

                        for item in allTargetFormats:
                                newTargetFormat = targetFormat()
                                newTargetFormat = item
                                newTargetFormat.active = True
                                newTargetFormat.access = True
                                printer.out("Enabling ["+item.name+"].")
                                all_targetformats.targetFormats.append(newTargetFormat)

                        result = self.api.Orgs(org.dbId).Targetformats.Updateaccess(body=all_targetformats)

                        if result is None or len(result.targetFormats.targetFormat) == 0:
                                printer.out("The target format(s) selected are already enabled", printer.WARNING)
                                return 0
                        sentenceReturn = "Target Format(s)"
                        for tf in result.targetFormats.targetFormat:
                                sentenceReturn = sentenceReturn + " " + tf.name + " "
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
                doParser = ArgumentParser(add_help = True, description="Disable one or more target formats for the provided organization.")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--targetFormats', dest='targetFormats', nargs='+', required=True, help="Target Format(s) for which the current command should be executed. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
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

                        printer.out("Getting target format list for ["+org.name+"] . . .")
                        allTargetFormats = self.api.Orgs(org.dbId).Targetformats.Getall()
                        allTargetFormats = allTargetFormats.targetFormats.targetFormat

                        if len(allTargetFormats) == 0:
                                printer.out("There is no target formats in ["+org.name+"].", printer.WARNING)
                                return 0

                        all_targetformats = targetFormats()
                        all_targetformats.targetFormats = pyxb.BIND()

                        allTargetFormats = compare(allTargetFormats, doArgs.targetFormats, "name")

                        if len(allTargetFormats) == 0:
                                listName = ""
                                for tfname in doArgs.targetFormats:
                                        listName = listName + tfname + " "
                                printer.out("There is no target formats matching ["+listName+"].", printer.ERROR)
                                return 2

                        for item in allTargetFormats:
                                newTargetFormat = targetFormat()
                                newTargetFormat = item
                                newTargetFormat.active = False
                                newTargetFormat.access = False
                                printer.out("Disabling ["+item.name+"].")
                                all_targetformats.targetFormats.append(newTargetFormat)

                        result = self.api.Orgs(org.dbId).Targetformats.Updateaccess(body=all_targetformats)

                        if result is None or len(result.targetFormats.targetFormat) == 0:
                                printer.out("The target format(s) selected are already disabled", printer.WARNING)
                                return 0
                        sentenceReturn = "Target Format(s)"
                        for tf in result.targetFormats.targetFormat:
                                sentenceReturn = sentenceReturn + " " + tf.name + " "
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
                doParser = ArgumentParser(add_help=True, description="Delete a target format in the organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--id', dest='id', type=str, required=True, help="Id of the target format to delete in the organization.")
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

                        printer.out("Getting target format with id ["+doArgs.id+"] for ["+org.name+"] . . .")
                        targetFormat = self.api.Orgs(org.dbId).Targetformats(doArgs.id).Get()
                        if targetFormat is None:
                                printer.out("targetFormat with id "+ doArgs.id +" does not exist", printer.ERROR)
                                return 2
                        else:
                                result = self.api.Orgs(org.dbId).Targetformats(doArgs.id).Delete()
                                printer.out("Target Format ["+targetFormat.name+"] has successfully been deleted.", printer.OK)

                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_delete()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_delete(self):
                doParser = self.arg_delete()
                doParser.print_help()