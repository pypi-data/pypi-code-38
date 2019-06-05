__author__="UShareSoft"

from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from ussclicore.cmd import Cmd, CoreGlobal
from texttable import Texttable
from uforgecli.utils.org_utils import org_get
from ussclicore.utils import generics_utils, printer
from uforgecli.utils.uforgecli_utils import *
from uforgecli.utils.compare_utils import compare
from uforgecli.utils.extract_id_utils import extractId
from hurry.filesize import size
from uforgecli.utils import *
from uforgecli.utils.texttable_utils import *
from uforgecli.commands.template.template_info import TemplateInfo
import shlex


class Template_Cmd(Cmd, CoreGlobal):
        """Administer templates for a user (list/info/create/delete/generate/share etc)"""

        cmd_name = "template"

        def __init__(self):
                super(Template_Cmd, self).__init__()

        def arg_list(self):
                doParser = ArgumentParser(add_help=True, description="List all the templates created by a user")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--account', dest='account', required=True, help="Name of the user")
                optional.add_argument('--os', dest='os', nargs='+', required=False, help="Only display templates that have been built from the operating system(s). You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--name',  dest='name', nargs='+', required=False, help="Only display templates that have the name matching this name. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")

                return doParser

        def do_list(self, args):
                try:
                        doParser = self.arg_list()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        userAppliances = self.api.Users(doArgs.account).Appliances.Getall()
                        if userAppliances.total == 0:
                                printer.out("[" + doArgs.account + "] has no template.")
                                return 0
                        userAppliances = userAppliances.appliances.appliance

                        if doArgs.os is not None:
                                userAppliances = compare(userAppliances, doArgs.os, "distributionName")
                        if doArgs.name is not None:
                                userAppliances = compare(userAppliances, doArgs.name, "name")

                        if len(userAppliances) == 0:
                                printer.out("No match with this filters.")
                                return 0
                        printer.out("List of templates created by [" + doArgs.account + "]:")
                        table = init_texttable(["Id", "Name", "Version", "OS", "Created", "Last Modified", "# Imgs", "Updates", "Imp", "Shd"],
                                               200,
                                               ["l", "l", "l", "l", "l", "l", "l", "l", "l", "l"],
                                               ["t", "a", "t", "a", "a", "a", "a", "a", "a", "a"])
                        for appliance in userAppliances:
                                created = appliance.created.strftime("%Y-%m-%d %H:%M:%S")
                                lastModified = appliance.lastModified.strftime("%Y-%m-%d %H:%M:%S")
                                if appliance.imported:
                                        imported = "X"
                                else:
                                        imported = ""
                                if appliance.shared:
                                        shared = "X"
                                else:
                                        shared = ""
                                if appliance.nbUpdates == -1:
                                       nbUpdates = 0
                                else:
                                       nbUpdates = appliance.nbUpdates
                                table.add_row([appliance.dbId, appliance.name, appliance.version, appliance.distributionName + " " + appliance.archName, created, lastModified, str(len(appliance.imageUris.uri)), nbUpdates, imported, shared])
                        print table.draw() + "\n"

                        return 0

                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_list()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_list(self):
                doParser = self.arg_list()
                doParser.print_help()

        def arg_info(self):
                doParser = ArgumentParser(add_help=True, description="Retrieve detailed information of a user's template")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--account', dest='account', required=True, help="Name of the user")
                mandatory.add_argument('--id', dest='id', required=True, help="The unique identifier of the template to retrieve")
                optional.add_argument('--all', action="store_true", dest='all', required=False, help="Print out more information contained in the template")

                return doParser

        def do_info(self, args):
                try:
                        doParser = self.arg_info()
                        doArgs = doParser.parse_args(shlex.split(args))

                        if not doArgs:
                                return 2

                        user_appliance = self.api.Users(doArgs.account).Appliances(doArgs.id).Get()

                        template_info = TemplateInfo(self.api, doArgs.account, user_appliance, doArgs.all)

                        template_info.print_main_info()
                        template_info.print_os_profile()
                        template_info.print_install_settings()
                        template_info.print_projects()
                        template_info.print_software()
                        template_info.print_configuration()

                        return 0

                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_info()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_info(self):
                doParser = self.arg_info()
                doParser.print_help()

        def arg_images(self):
                doParser = ArgumentParser(add_help=True, description="Retrieve list of images generated from the template")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--account', dest='account', required=True, help="Name of the user.")
                mandatory.add_argument('--id', dest='id', required=True, help="Id of the appliance.")
                optional.add_argument('--os', dest='os', nargs='+', required=False, help="Only display images that have been built from the operating system(s). You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--name',  dest='name', nargs='+', required=False, help="Only display images that have the name matching this name. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--targetFormat',  dest='targetFormat', nargs='+', required=False, help="Only display images that have been generated by the following format(s). You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                return doParser

        def do_images(self, args):
                try:
                        doParser = self.arg_images()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        printer.out("Getting images list...")
                        allImages = self.api.Users(doArgs.account).Appliances(doArgs.id).Images.Getall()

                        appliancesList = self.api.Users(doArgs.account).Appliances.Getall()
                        appliancesList = appliancesList.appliances.appliance

                        if allImages is None or len(allImages.images.image) == 0:
                                printer.out("No images found for user [" + doArgs.account + "].")
                                return 0

                        allImages = generics_utils.order_list_object_by(allImages.images.image, "name")

                        if doArgs.name is not None:
                                allImages = compare(allImages, doArgs.name, "name")
                        if doArgs.targetFormat is not None:
                                allImages = compare(allImages, doArgs.targetFormat, "targetFormat", "name")
                        if doArgs.os is not None:
                                allImages = compare(list=allImages, values=doArgs.os, attrName='distributionName', subattrName=None, otherList=appliancesList, linkProperties=['applianceUri', 'uri'])

                        if allImages is None or len(allImages) == 0:
                                printer.out("No images found for user [" + doArgs.account + "] with these filters.")
                                return 0

                        printer.out("Images list :")
                        table = init_texttable(["Id", "Name", "Version", "Rev", "OS", "Format", "Created", "Size", "Compressed", "Status"],
                                               200,
                                               ["l", "l", "l", "l", "l", "l", "l", "l", "l", "l"],
                                               ["t", "a", "t", "a", "a", "a", "a", "a", "a", "a"])
                        for image in allImages:
                                created = image.created.strftime("%Y-%m-%d %H:%M:%S")
                                if image.compress:
                                        compressed = "X"
                                else:
                                        compressed = ""
                                if image.status.error:
                                        status = "Error"
                                elif image.status.cancelled:
                                        status = "Cancelled"
                                elif image.status.complete:
                                        status = "Done"
                                else:
                                        status = "Generating"
                                appliance = self.api.Users(doArgs.account).Appliances(doArgs.id).Get()
                                osImage = appliance.distributionName + " " + appliance.archName
                                table.add_row([image.dbId, image.name, image.version, image.revision, osImage, image.targetFormat.name, created, size(image.size), compressed, status])
                        print table.draw() + "\n"

                        printer.out("Found " + str(len(allImages)) + " images.")
                        return 0

                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_images()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_images(self):
                doParser = self.arg_images()
                doParser.print_help()

        def arg_pimages(self):
                doParser = ArgumentParser(add_help=True, description="Retrieve list of images published to cloud environments from the template")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--account', dest='account', required=True, help="Name of the user.")
                mandatory.add_argument('--id', dest='id', required=True, help="Id of the appliance.")
                optional.add_argument('--os', dest='os', nargs='+', required=False, help="Only display images that have been built from the operating system(s). You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--name',  dest='name', nargs='+', required=False, help="Only display images that have the name matching this name. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--targetFormat',  dest='targetFormat', nargs='+', required=False, help="Only display images that have been generated by the following format(s). You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")

                return doParser

        def do_pimages(self, args):
                try:
                        doParser = self.arg_pimages()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        printer.out("Getting published images list...")
                        allPimages = self.api.Users(doArgs.account).Appliances(doArgs.id).Pimages.Getall()

                        appliancesList = self.api.Users(doArgs.account).Appliances.Getall()
                        appliancesList = appliancesList.appliances.appliance

                        if allPimages is None or allPimages == "" or len(allPimages.publishImages.publishImage) == 0:
                                printer.out("No published image found.")
                                return 0
                        allPimages = generics_utils.order_list_object_by(allPimages.publishImages.publishImage, "name")

                        if doArgs.name is not None:
                                allPimages = compare(allPimages, doArgs.name, "name")
                        if doArgs.targetFormat is not None:
                                allPimages = compare(allPimages, doArgs.targetFormat, "targetFormat", "name")
                        if doArgs.os is not None:
                                allPimages = compare(list=allPimages, values=doArgs.os, attrName='distributionName', subattrName=None, otherList=appliancesList, linkProperties=['applianceUri', 'uri'])

                        printer.out("Published images list :")
                        table = init_texttable(["Id", "Name", "Version", "Rev", "OS", "Cloud", "Published", "Size", "Status"],
                                               200,
                                               ["l", "l", "l", "l", "l", "l", "l", "l", "l"],
                                               ["a", "a", "t", "a", "a", "a", "a", "a", "a"])
                        for image in allPimages:
                                cloud = image.created.strftime("%Y-%m-%d %H:%M:%S")
                                if image.status.error:
                                        status = "Error"
                                elif image.status.cancelled:
                                        status = "Cancelled"
                                elif image.status.complete:
                                        status = "Done"
                                else:
                                        status = "Generating"
                                appliance = self.api.Users(doArgs.account).Appliances(doArgs.id).Get()
                                osImage = appliance.distributionName + " " + appliance.archName
                                table.add_row([image.dbId, image.name, image.version, image.revision, osImage, image.credAccount.targetPlatform.name, cloud, size(image.size), status])
                        print table.draw() + "\n"
                        return 0

                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_pimages()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_pimages(self):
                doParser = self.arg_pimages()
                doParser.print_help()
