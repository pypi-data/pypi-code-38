
__author__="UShareSoft"

from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from ussclicore.cmd import Cmd, CoreGlobal
from texttable import Texttable
from ussclicore.utils import generics_utils, printer
from uforgecli.utils.uforgecli_utils import *
from uforgecli.utils import *
from hurry.filesize import size
from uforgecli.utils.extract_id_utils import extractId
from uforgecli.utils.compare_utils import compare
from uforgecli.utils.texttable_utils import *
import shlex


class Pimages_Cmd(Cmd, CoreGlobal):
        """Administer published images for a user"""

        cmd_name = "pimages"

        def __init__(self):
                super(Pimages_Cmd, self).__init__()

        def arg_list(self):
                doParser = ArgumentParser(add_help=True, description="List all the published images created by a user")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--account', dest='account', required=True, help="Name of the user.")
                optional.add_argument('--os', dest='os', nargs='+', required=False, help="Only display published images that have been built from the operating system(s). You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--name', dest='name', nargs='+', required=False, help="Only display published images that have the name matching this name. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                optional.add_argument('--cloud', dest='cloud', nargs='+', required=False, help="Only display published images that have been published to the following cloud environment(s). You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")

                return doParser

        def do_list(self, args):
                try:
                        doParser = self.arg_list()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        printer.out("Getting published images ...")
                        allPimages = self.api.Users(doArgs.account).Pimages.Getall()
                        allPimages = allPimages.publishImages.publishImage

                        userAppliances = self.api.Users(doArgs.account).Appliances.Getall()
                        userAppliances = userAppliances.appliances.appliance

                        if allPimages is None or len(allPimages) == 0:
                                printer.out("No publish images for user [" + doArgs.account + "].")
                                return 0

                        if doArgs.name:
                                allPimages = compare(allPimages, doArgs.name, "name")

                        if doArgs.os is not None:
                                allPimages = compare(list=allPimages, values=doArgs.os, attrName='distributionName', subattrName=None, otherList=userAppliances, linkProperties=['applianceUri', 'uri'])

                        if doArgs.cloud is not None:
                                allPimages = compare(list=allPimages, values=doArgs.cloud, attrName='targetFormat', subattrName='name')

                        if len(allPimages) == 0:
                                printer.out("There is no publish images for user [" + doArgs.account + "] with these filters.")
                                return 0

                        table = init_texttable(["Id", "Name", "Version", "Rev", "OS", "Cloud", "Published", "Size", "Status"],
                                               200,
                                               ["l", "l", "l", "l", "l", "l", "l", "l", "l"],
                                               ["a", "a", "t", "a", "a", "a", "a", "a", "a"])
                        for item in allPimages:
                                if item.status.error:
                                        status = "Error"
                                elif item.status.cancelled:
                                        status = "Cancelled"
                                elif item.status.complete:
                                        status = "Done"
                                else:
                                        status = "Publishing"
                                for item2 in userAppliances:
                                        if item.parentUri == item2.uri:
                                                os = item2.distributionName + " " + item2.archName
                                table.add_row([item.dbId, item.name, item.version, item.revision, os, item.credAccount.targetPlatform.name, item.created.strftime("%Y-%m-%d %H:%M:%S"), size(item.size), status])
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
                doParser = ArgumentParser(add_help=True, description="Retrieve detailed information of a published image")

                mandatory = doParser.add_argument_group("mandatory arguments")

                mandatory.add_argument('--account', dest='account', required=True, help="Name of the user.")
                mandatory.add_argument('--id', dest='id', required=True, help="The unique identifier of the published image to retrieve.")

                return doParser

        def do_info(self, args):
                try:
                        doParser = self.arg_info()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        allPimages = self.api.Users(doArgs.account).Pimages.Getall()
                        userAppliances = self.api.Users(doArgs.account).Appliances.Getall()

                        printer.out("Getting published image with id [" + doArgs.id + "] ...")

                        Exist = False
                        for item in allPimages.publishImages.publishImage:
                                if str(item.dbId) == str(doArgs.id):
                                        printer.out("Published image informations :")
                                        for item2 in userAppliances.appliances.appliance:
                                                if item.parentUri == item2.uri:
                                                        os = item2.distributionName + " " + item2.archName
                                                        description = item2.description
                                        if item.status.published:
                                                published = "Yes"
                                        else:
                                                published = "No"
                                        Exist = True
                                        table = init_texttable(None, 200, ["l", "l"], ["a", "t"])
                                        table.add_row(["Name", item.name])
                                        table.add_row(["Id", item.dbId])
                                        table.add_row(["Cloud", item.credAccount.targetPlatform.name])
                                        table.add_row(["Version", item.version])
                                        table.add_row(["Revision", item.revision])
                                        table.add_row(["Uri", item.uri])
                                        table.add_row(["OS", os])
                                        table.add_row(["Template ID", extractId(item.uri)])
                                        table.add_row(["Generated Image Id", extractId(item.imageUri)])
                                        table.add_row(["Created", item.created.strftime("%Y-%m-%d %H:%M:%S")])
                                        table.add_row(["Size", size(item.size)])
                                        table.add_row(["Description", description])
                                        table.add_row(["Published", published])
                                        table.add_row(["Published Cloud Id", item.cloudId])
                                        print table.draw() + "\n"

                                        table = Texttable(200)
                                        table.set_cols_align(["l", "l"])
                                        table.header(["Cloud Target Details", ""])
                                        table = self.print_cloud_fields(publishImage=item,table=table)
                                        print table.draw() + "\n"

                                        table = Texttable(200)
                                        table.set_cols_align(["l", "l"])
                                        table.header(["Status Details", ""])
                                        if item.status.error:
                                                status = "Error"
                                        elif item.status.cancelled:
                                                status = "Cancelled"
                                        elif item.status.complete:
                                                status = "Done"
                                        else:
                                                status = "Publishing"
                                        table.add_row(["Status", status])
                                        if item.status.error:
                                                table.add_row(["Error Message", item.status.message])
                                                table.add_row(["Detailed Error Message", item.status.detailedErrorMsg])
                                        else:
                                                table.add_row(["Message", item.status.message])

                                        print table.draw() + "\n"

                        if not Exist:
                                printer.out("Published image with ID [" + doArgs.id + "] was not found.")

                        return 0

                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_info()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_info(self):
                doParser = self.arg_info()
                doParser.print_help()

        def print_cloud_fields(self, publishImage, table):
            if publishImage.credAccount.targetPlatform.type == "aws":
                self.print_amazon(publishImage, table)
            elif publishImage.credAccount.targetPlatform.type == "vsphere":
                self.print_vsphere(publishImage, table)
            elif publishImage.credAccount.targetPlatform.type == "vclouddirector":
                self.print_vcd(publishImage, table)
            elif publishImage.credAccount.targetPlatform.type == "openstack":
                self.print_openstack(publishImage, table)
            elif publishImage.credAccount.targetPlatform.type == "cloudstack":
                self.print_cloudstack(publishImage, table)
            elif publishImage.credAccount.targetPlatform.type == "azure":
                self.print_azure(publishImage, table)
            elif publishImage.credAccount.targetPlatform.type == "google":
                self.print_google(publishImage, table)
            elif publishImage.credAccount.targetPlatform.type == "outscale":
                self.print_outscale(publishImage, table)
            else:
                self.print_susecloud(publishImage, table)
            return table


        def print_outscale(self, publishImage, table):
            table.add_row(["Access Key ID", publishImage.credAccount.accessKeyId])
            table.add_row(["Secret Access Key", publishImage.credAccount.secretAccessKeyId])

        def print_susecloud(self, publishImage, table):
            table.add_row(["Glance Url", str(publishImage.credAccount.glanceUrl)])
            table.add_row(["Keystone Url", str(publishImage.credAccount.keystoneUrl)])
            table.add_row(["Login", publishImage.credAccount.login])
            table.add_row(["Password", publishImage.credAccount.password])
            
        def print_amazon(self, publishImage, table):
            table.add_row(["Account Number", publishImage.credAccount.accountNumber])
            table.add_row(["Access Key ID", publishImage.credAccount.accessKeyId])
            table.add_row(["Secret Access Key", publishImage.credAccount.secretAccessKeyId])
            table.add_row(["Key Pair Name", publishImage.credAccount.keyPairName])

        def print_vsphere(self, publishImage, table):
            table.add_row(["vSphere Server", publishImage.credAccount.hostname])
            table.add_row(["Login", publishImage.credAccount.login])
            table.add_row(["Password", publishImage.credAccount.password])
            table.add_row(["Port", publishImage.credAccount.proxyPort])
            table.add_row(["Proxy Host", publishImage.credAccount.proxyHost])
            table.add_row(["Proxy Port", publishImage.credAccount.proxyPort])

        def print_vcd(self, publishImage, table):
            table.add_row(["VCloud Director Server", publishImage.credAccount.hostname])
            table.add_row(["Login", publishImage.credAccount.login])
            table.add_row(["Password", publishImage.credAccount.password])
            table.add_row(["Port", publishImage.credAccount.proxyPort])
            table.add_row(["Proxy Host", publishImage.credAccount.proxyHost])
            table.add_row(["Proxy Port", publishImage.credAccount.proxyPort])

        def print_cloudstack(self, publishImage, table):
            table.add_row(["Endpoint Url", str(publishImage.credAccount.endpointUrl)])
            table.add_row(["Public API Key", publishImage.credAccount.publicApiKey])
            table.add_row(["Secret API Key", publishImage.credAccount.secretApiKey])

        def print_openstack(self, publishImage, table):
            table.add_row(["Glance Url", str(publishImage.credAccount.glanceUrl)])
            table.add_row(["Keystone Url", str(publishImage.credAccount.keystoneUrl)])
            table.add_row(["Keystone Version", publishImage.credAccount.keystoneVersion])
            table.add_row(["Login", publishImage.credAccount.login])
            table.add_row(["Password", publishImage.credAccount.password])

        def print_azure(self, publishImage, table):
            table.add_row(["Account Name", publishImage.credAccount.accountName])

        def print_google(self, publishImage, table):
            table.add_row(["Account Name", publishImage.credAccount.accountName])
            table.add_row(["Login Name", publishImage.credAccount.login])