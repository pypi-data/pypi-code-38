__author__="UShareSoft"

from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from ussclicore.cmd import Cmd, CoreGlobal
from texttable import Texttable
from uforgecli.utils.org_utils import org_get
from ussclicore.utils import generics_utils, printer, ascii_bar_graph
from uforgecli.utils.uforgecli_utils import *
from uforgecli.utils import *
from hurry.filesize import size,alternative
from uforgecli.utils import constants
from uforgecli.utils import quota_utils
import shlex



class User_Quota_Cmd(Cmd, CoreGlobal):
        """List the status of all the quotas that can be set for the user (disk usage, generations, scans and number of templates)"""

        cmd_name = "quota"

        def __init__(self):
                super(User_Quota_Cmd, self).__init__()

        def arg_list(self):
                doParser = ArgumentParser(add_help = True, description="Displays the user's quota information")
                mandatory = doParser.add_argument_group("mandatory arguments")
                mandatory.add_argument('--account', dest='account', type=str, required=True, help="User name of the account to see quotas")
                return doParser

        def do_list(self, args):
                try:
                        doParser = self.arg_list()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        #call UForge API
                        printer.out("Getting quotas for ["+doArgs.account+"] ...")
                        quotas = self.api.Users(doArgs.account).Quotas.Get()
                        if quotas is None or len(quotas.quotas.quota) == 0:
                                printer.out("No quotas available for ["+doArgs.account+"].")
                        else:
                                printer.out("List of quotas available for ["+doArgs.account+"] :")
                                quotas = generics_utils.order_list_object_by(quotas.quotas.quota, "type")
                                table = Texttable(200)
                                table.set_cols_align(["c", "c", "c","c", "c"])
                                table.header(["Type", "Consumed", "Limit", "Frequency", "Renewal date"])
                                for item in quotas:
                                        if item.limit == -1:
                                                limit = "unlimited"
                                        else:
                                                limit = item.limit
                                        if item.nb > 1:
                                                name = item.type+"s"
                                        else:
                                                name = item.type
                                        if item.frequency is None:
                                                frequency = "-"
                                        else:
                                                frequency = item.frequency
                                        if item.renewalDate is None:
                                                renewalDate = "-"
                                        else:
                                                renewalDate = item.renewalDate
                                        if constants.QUOTAS_DISK_USAGE == item.type:
                                                table.add_row([name, size(item.nb, system=alternative), size(limit, system=alternative) if limit != "unlimited" else limit , frequency, renewalDate])
                                        else:
                                                table.add_row([name, item.nb,limit, frequency, renewalDate])
                                print table.draw() + "\n"

                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_list()
                        return 0

                except Exception as e:
                        return handle_uforge_exception(e)

        def help_list(self):
                doParser = self.arg_list()
                doParser.print_help()

        def arg_modify(self):
                doParser = ArgumentParser(add_help = True, description="Modify a user quota")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--account', dest='account', type=str, required=True, help="user name of the account for which the current command should be executed")
                mandatory.add_argument('--type', dest='type', type=str, required=False, help="Quota type. Possible values: appliance|generation|scan|diskusage)")

                optional.add_argument('--unlimited', dest='unlimited', action="store_true", required=False, help="Flag to remove any quota from a resource (becomes unlimited)")
                optional.add_argument('--limit', dest='limit', type=int, required=False, help="Quota limit (ex: --limit 10).  Note, for disk usage this is in bytes.")
                optional.add_argument('--nb', dest='nb', type=int, required=False, help="Set the current consumption of a resource including appliance templates, generations, scans and disk usage (ex: --nb 2). This can be used for discounts or in the case of errors etc")
                optional.add_argument('--frequency', dest='frequency', type=str, required=False, help="the frequency the consumption counter of a resource will be reset.  Possible values are none|monthly.  For example, if you wish to allow a user to have 5 generations per month, '--limit 5 --frequency monthly")
                return doParser

        def do_modify(self, args):
                try:
                        doParser = self.arg_modify()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        if not doArgs.unlimited and doArgs.limit is None and doArgs.nb is None:
                                printer.out("You must specify a modification (unlimited|limit|nb).", printer.ERROR)
                                return 2
                        printer.out("Getting quotas for ["+doArgs.account+"] ...")
                        quotas = self.api.Users(doArgs.account).Quotas.Get()

                        if quotas is None or len(quotas.quotas.quota) == 0 :
                                printer.out("No quotas available for ["+doArgs.account+"].", printer.ERROR)
                        else:
                                typeExist = False
                                for item in quotas.quotas.quota:
                                        if item.type == doArgs.type:
                                                typeExist = True
                                                if doArgs.nb is not None:
                                                        item.nb = doArgs.nb
                                                quota_utils.validate(doArgs)
                                                quota_utils.update(item, doArgs)

                                if not typeExist:
                                        printer.out("Type is not defined or correct.", printer.ERROR)
                                        return 2
                                else:
                                        quotas = self.api.Users(doArgs.account).Quotas.Update(body=quotas)
                                        printer.out("Changes done.", printer.OK)

                                        quotas = generics_utils.order_list_object_by(quotas.quotas.quota, "type")
                                        table = Texttable(200)
                                        table.set_cols_align(["c", "c", "c","c", "c"])
                                        table.header(["Type", "Consumed", "Limit", "Frequency", "Renewal date"])
                                        for item in quotas:
                                                if item.limit == -1:
                                                        limit = "unlimited"
                                                else:
                                                        limit = item.limit
                                                if item.nb > 1:
                                                        name = item.type+"s"
                                                else:
                                                        name = item.type
                                                if item.frequency is None:
                                                        frequency = "-"
                                                else:
                                                        frequency = item.frequency
                                                if item.renewalDate is None:
                                                        renewalDate = "-"
                                                else:
                                                        renewalDate = item.renewalDate
                                                if constants.QUOTAS_DISK_USAGE == item.type:
                                                        table.add_row([name, size(item.nb, system=alternative), size(limit, system=alternative) if limit != "unlimited" else limit , frequency, renewalDate])
                                                else:
                                                        table.add_row([name, item.nb,limit, frequency, renewalDate])
                                        print table.draw() + "\n"
                        return 0

                except ValueError as e:
                        printer.out(str(e), printer.ERROR)
                        self.help_modify()
                        return 2
                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_modify()
                        return 2
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_modify(self):
                doParser = self.arg_modify()
                doParser.print_help()
