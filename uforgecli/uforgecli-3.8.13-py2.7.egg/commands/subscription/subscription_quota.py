__author__ = "UShareSoft"

from texttable import Texttable
from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from ussclicore.cmd import Cmd, CoreGlobal
from uforgecli.utils import org_utils
from ussclicore.utils import printer
from ussclicore.utils import generics_utils
from uforgecli.utils.uforgecli_utils import *
from uforge.objects import uforge
from uforgecli.utils import uforgecli_utils
from uforgecli.utils import quota_utils
import pyxb
import shlex


class Subscription_Quota(Cmd, CoreGlobal):
        """Manage subscription profile quotas"""

        cmd_name = "quota"

        def __init__(self):
                super(Subscription_Quota, self).__init__()

        def arg_update(self):
                doParser = ArgumentParser(prog=self.cmd_name + " update", add_help=True, description="Updates a subscription profile quota.")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--name', dest='name', required=True, help="The name of the subscription profile")
                mandatory.add_argument('--type', dest='type', required=True, help="Quota type. Possible values: appliance|generation|scan|diskusage")
                optional.add_argument('--org', dest='org', required=False, help="The organization name. If no organization is provided, then the default organization is used.")
                optional.add_argument('--unlimited',  dest='unlimited', action="store_true", required=False, help="Flag to remove any quota from a resource (becomes unlimited)")
                optional.add_argument('--limit', dest='limit', required=False, help="Quota limit (ex: --limit 10).  Note, disk usage is in bytes.")
                optional.add_argument('--frequency', dest='frequency', required=False, help="The frequency at which a consumption counter for a resource will be reset.  Possible values are none|monthly.  For example, if you wish to allow a user to have 5 generations per month, '--limit 5 --frequency monthly'")
                return doParser

        #The update can sometimes create a quota, because in database an empty quota is by default an unlimited quota.
        #To modify this unlimited quota, we have to create it and then update the fields. This behavior can be discussed because it might be missleading for developers ...
        def do_update(self, args):
                try:
                        # add arguments
                        doParser = self.arg_update()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        if not doArgs.unlimited and doArgs.limit is None:
                                printer.out("You must specify a modification (unlimited|limit).", printer.ERROR)
                                return 2

                        quota_utils.validate(doArgs)

                        printer.out("Getting subscription profile with name [" + doArgs.name + "]...")
                        org = org_utils.org_get(self.api, doArgs.org)
                        subscriptions = self.api.Orgs(org.dbId).Subscriptions().Getall(Search=doArgs.name)

                        if subscriptions is None or len(subscriptions.subscriptionProfiles.subscriptionProfile) == 0:
                                printer.out("No subscription with name [" + doArgs.name + "].", printer.ERROR)
                                return 2
                        subscription = subscriptions.subscriptionProfiles.subscriptionProfile[0]

                        quotaList = quotas()
                        quotaList.quotas = pyxb.BIND()

                        updatedQuota = False

                        for item in subscription.quotas.quota:
                                if item.type == doArgs.type:
                                        quota_utils.update(item, doArgs)
                                        updatedQuota = True
                                quotaList.quotas.append(item)

                        #If the quota to be updated is not found we have to create it
                        if not updatedQuota:
                                printer.out("Creating quota for subscription profile with name [" + doArgs.name + "]...")
                                newQuota = quota()
                                quota_utils.update(newQuota, doArgs)
                                quotaList.quotas.append(newQuota)

                        # call UForge API
                        self.api.Orgs(org.dbId).Subscriptions(subscription.dbId).Quotas.Update(quotaList)
                        printer.out("Quotas has been updated.", printer.OK)
                        return 0

                except pyxb.SimpleFacetValueError:
                        printer.out("Type is not defined or correct.", printer.ERROR)
                        self.help_update()
                        return 2
                except ValueError as e:
                        printer.out(str(e), printer.ERROR)
                        self.help_update()
                        return 2
                except ArgumentParserError as e:
                        printer.out("In Arguments: " + str(e), printer.ERROR)
                        self.help_update()
                        return 2
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_update(self):
                doParser = self.arg_update()
                doParser.print_help()