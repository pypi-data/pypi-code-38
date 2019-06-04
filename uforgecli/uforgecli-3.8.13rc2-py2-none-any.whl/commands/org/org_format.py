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

class Org_Format_Cmd(Cmd, CoreGlobal):
        """Format operation (list|enable|disable)"""

        cmd_name = "format"

        def __init__(self):
                super(Org_Format_Cmd, self).__init__()

        def arg_list(self):
                doParser = ArgumentParser(add_help = True, description="List all the formats (enabled and disabled) for the provided organization")

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
                        printer.out("Getting user list for ["+org.name+"] . . .")
                        allFormats = self.api.Orgs(org.dbId).Formats.Getall()
                        allFormats = order_list_object_by(allFormats.imageFormats.imageFormat, "name")

                        if len(allFormats) == 0:
                                printer.out("There is no formats in ["+org.name+"].")
                                return 0

                        table = Texttable(200)
                        table.set_cols_align(["l", "l", "l", "c"])
                        table.header(["Id", "Format", "Access", "Default"])

                        for item in allFormats:
                                if item.access:
                                        access = "X"
                                else:
                                        access = ""
                                if item.preselected:
                                        preselected = "X"
                                else:
                                        preselected = ""
                                table.add_row([item.dbId, item.name, access, preselected])

                        print table.draw() + "\n"
                        printer.out("Found "+str(len(allFormats))+" formats.")
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
                doParser = ArgumentParser(add_help = True, description="Enable one or more formats for the provided organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")
                mandatory.add_argument('--formats', dest='format', nargs='+', required=True, help="Format(s) for which the current command should be executed. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                return doParser

        def do_enable(self, args):
                try:
                        doParser = self.arg_enable()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)
                        printer.out("Getting format list for ["+org.name+"] . . .")
                        allFormats = self.api.Orgs(org.dbId).Formats.Getall()
                        allFormats = allFormats.imageFormats.imageFormat

                        if len(allFormats) == 0:
                                printer.out("There is no formats in ["+org.name+"].")
                                return 0

                        all_formats = imageFormats()
                        all_formats.imageFormats = pyxb.BIND()

                        allFormats = compare(allFormats, doArgs.format, "name")

                        for item in allFormats:
                                newFormat = imageFormat()
                                newFormat = item
                                newFormat.access = True
                                newFormat.active = True
                                printer.out("Enabling ["+item.name+"].")
                                all_formats.imageFormats.append(newFormat)

                        result = self.api.Orgs(org.dbId).Formats.Update(body=all_formats)

                        if result is None or len(result.imageFormats.imageFormat) == 0:
                                printer.out("The format(s) selected are already enabled", printer.WARNING)
                                return 0
                        sentenceReturn = "Format(s)"
                        for format in result.imageFormats.imageFormat:
                                sentenceReturn = sentenceReturn + " " + format.name + " "
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
                doParser = ArgumentParser(add_help = True, description="Disable one or more formats for the provided organization. Disabling will remove this as a 'default' format")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")
                mandatory.add_argument('--formats', dest='format', nargs='+', required=True, help="Format(s) for which the current command should be executed. You can use Unix matching system (*,?,[seq],[!seq]) and multiple match separating by space.")
                return doParser

        def do_disable(self, args):
                try:
                        doParser = self.arg_disable()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)
                        printer.out("Getting format list for ["+org.name+"] . . .")
                        allFormats = self.api.Orgs(org.dbId).Formats.Getall()
                        allFormats = allFormats.imageFormats.imageFormat

                        if len(allFormats) == 0:
                                printer.out("There is no formats in ["+org.name+"].")
                                return 0

                        all_formats = imageFormats()
                        all_formats.imageFormats = pyxb.BIND()

                        allFormats = compare(allFormats, doArgs.format, "name")

                        for item in allFormats:
                                newFormat = imageFormat()
                                newFormat = item
                                newFormat.access = False
                                newFormat.active = False
                                newFormat.preselected = False
                                printer.out("Disabling ["+item.name+"].")
                                all_formats.imageFormats.append(newFormat)

                        result = self.api.Orgs(org.dbId).Formats.Update(body=all_formats)

                        if result is None or len(result.imageFormats.imageFormat) == 0:
                                printer.out("The format(s) selected are already disabled", printer.WARNING)
                                return 0
                        sentenceReturn = "Format(s)"
                        for format in result.imageFormats.imageFormat:
                                sentenceReturn = sentenceReturn + " " + format.name + " "
                        printer.out(sentenceReturn + "have/has been disabled.", printer.OK)
                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_disable()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_disable(self):
                doParser = self.arg_disable()
                doParser.print_help()