__author__ = "UShareSoft"

from texttable import Texttable
from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from ussclicore.cmd import Cmd, CoreGlobal
from uforgecli.utils import org_utils
from ussclicore.utils import printer
from ussclicore.utils import generics_utils
from ussclicore.utils.generics_utils import order_list_object_by
from uforgecli.utils.uforgecli_utils import *
from uforge.objects import uforge
from hurry.filesize import size,alternative
from subscription_admin import Subscription_Admins
from subscription_role import Subscription_Roles
from subscription_os import Subscription_Os
from subscription_quota import Subscription_Quota
from subscription_targetPlatform import Subscription_TargetPlatform
from subscription_targetFormat import Subscription_TargetFormat
from uforgecli.utils import uforgecli_utils
from uforgecli.utils import constants
import pyxb
import shlex
import sys


class Subscription_Cmd(Cmd, CoreGlobal):
        """Manage subscription profiles : list profile, create profiles, update profiles"""

        cmd_name = "subscription"

        def __init__(self):
                self.subCmds = {}
                self.generate_sub_commands()
                super(Subscription_Cmd, self).__init__()

        def generate_sub_commands(self):
                subscriptionRoles = Subscription_Roles()
                self.subCmds[subscriptionRoles.cmd_name] = subscriptionRoles

                subscriptionAdmins = Subscription_Admins()
                self.subCmds[subscriptionAdmins.cmd_name] = subscriptionAdmins

                subscriptionOs = Subscription_Os()
                self.subCmds[subscriptionOs.cmd_name] = subscriptionOs

                subscriptionQuota = Subscription_Quota()
                self.subCmds[subscriptionQuota.cmd_name] = subscriptionQuota

                subscriptionTargetPlatform = Subscription_TargetPlatform()
                self.subCmds[subscriptionTargetPlatform.cmd_name] = subscriptionTargetPlatform

                subscriptionTargetFormat = Subscription_TargetFormat()
                self.subCmds[subscriptionTargetFormat.cmd_name] = subscriptionTargetFormat

        def arg_list(self):
                doParser = ArgumentParser(prog=self.cmd_name + " list", add_help=True, description="List all the subscription profiles for a given organization.  If no organization is provided the default organization is used.")

                optional = doParser.add_argument_group("optional arguments")

                optional.add_argument('--org', dest='org', required=False, help="The organization name. If no organization is provided, then the default organization is used.")
                return doParser

        def do_list(self, args):
                try:
                        doParser = self.arg_list()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)

                        # call UForge API
                        printer.out("Getting all the subscription profiles for organization ...")
                        subscriptions = self.api.Orgs(org.dbId).Subscriptions().Getall(Search=None)
                        subscriptions = generics_utils.order_list_object_by(subscriptions.subscriptionProfiles.subscriptionProfile, "name")
                        if subscriptions is None or len(subscriptions) == 0:
                                printer.out("There is no subscriptions in [" + org.name + "] ")
                                return 0
                        printer.out("List of subscription profiles in [" + org.name + "] :")
                        table = Texttable(200)
                        table.set_cols_align(["c", "c", "c", "c", "c"])
                        table.header(["Id", "Name", "Code", "Active", "description"])
                        for subscription in subscriptions:
                                if subscription.active:
                                        active = "X"
                                else:
                                        active = ""
                                table.add_row([subscription.dbId, subscription.name, subscription.code, active, subscription.description])
                        print table.draw() + "\n"
                        printer.out("Foumd " + str(len(subscriptions)) + " subscription profile(s).")
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
                doParser = ArgumentParser(prog=self.cmd_name + " info", add_help=True, description="Get detailed information on a subscription profile within an organization.")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--name', dest='name', required=True, help="The name of the subscription profile")
                optional.add_argument('--org', dest='org', required=False, help="The organization name. If no organization is provided, then the default organization is used.")
                return doParser

        def do_info(self, args):
                try:
                        # add arguments
                        doParser = self.arg_info()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        # call UForge API
                        printer.out("Getting subscription profile with name [" + doArgs.name + "]...")
                        org = org_utils.org_get(self.api, doArgs.org)

                        subscriptions = self.api.Orgs(org.dbId).Subscriptions().Getall(Search=None)
                        # only use to retrieve quota type list
                        userQuotas = self.api.Users(self.api._username).Quotas.Get()
                        printer.out("Subscription profile for [" + doArgs.name + "] :")
                        subscription = subscriptions.subscriptionProfiles.subscriptionProfile
                        exist = False
                        for item in subscription:
                                if item.name == doArgs.name:
                                        exist = True
                                        subscription = item

                        if not exist:
                                printer.out("Subscription profile requested don't exist in [" + org.name + "]")
                                return 0

                        table = Texttable(200)
                        table.set_cols_align(["l", "l"])
                        table.header(["Info", "Value"])
                        table.add_row(["Name", subscription.name])
                        table.add_row(["Code", subscription.code])

                        if subscription.active:
                                active = "X"
                        else:
                                active = ""
                        table.add_row(["Active", active])

                        if subscription.roles.role:
                                nb = len(subscription.roles.role)
                                table.add_row(["Roles", str(nb)])
                        else:
                                table.add_row(["Roles", "None"])

                        if subscription.admins.admin:
                                nbAdmin = len(subscription.admins.admin)
                                table.add_row(["Administrators", str(nbAdmin)])
                        else:
                                table.add_row(["Administrators", "None"])

                        if subscription.distributions.distribution:
                                nbDist = len(subscription.distributions.distribution)
                                table.add_row(["Operating Systems", str(nbDist)])
                        else:
                                table.add_row(["Operating Systems", "None"])

                        if subscription.targetFormats.targetFormat:
                                nbFormat = len(subscription.targetFormats.targetFormat)
                                table.add_row(["Target Formats", str(nbFormat)])
                        else:
                                table.add_row(["Target Formats", "None"])

                        if subscription.targetPlatforms.targetPlatform:
                                nbPlatform = len(subscription.targetPlatforms.targetPlatform)
                                table.add_row(["Target Platforms", str(nbPlatform)])
                        else:
                                table.add_row(["Target Platforms", "None"])

                        print table.draw() + "\n"

                        if subscription.description is not None or subscription.description == "":
                                printer.out("Description : " + subscription.description + "\n")

                        if subscription.admins.admin:
                                nb = subscription.admins.admin
                                nb = len(nb)
                                printer.out("Administrator Details :")

                                table = Texttable(200)
                                table.set_cols_align(["l"])
                                table.header(["Name"])
                                for item in subscription.admins.admin:
                                        table.add_row([item.name])
                                print table.draw() + "\n"
                                printer.out("Found " + str(nb) + " administrator(s).\n")
                        else:
                                printer.out("Subscription profile doesn't have any administrator.\n")

                        if subscription.roles.role:
                                printer.out("Role Details :")

                                table = Texttable(200)
                                table.set_cols_align(["l"])
                                table.header(["Name"])
                                for item in subscription.roles.role:
                                        table.add_row([item.name])
                                print table.draw() + "\n"
                        else:
                                printer.out("Subscription profile doesn't have any roles.\n")

                        if subscription.distributions.distribution:
                                nb = subscription.distributions.distribution
                                nb = len(nb)
                                printer.out("Operating system Details :")
                                table = Texttable(200)
                                table.set_cols_align(["l", "l", "l", "l", "l", "l"])
                                table.header(["Distribution", "Version", "Architecture", "Access", "Visible", "Release Date"])

                                for item in subscription.distributions.distribution:
                                        if item.active:
                                                active = "X"
                                        else:
                                                active = ""

                                        if item.visible:
                                                visible = "X"
                                        else:
                                                visible = ""

                                        if item.releaseDate is None:
                                                releaseDate = "Unknown"
                                        else:
                                                releaseDate = item.releaseDate
                                        table.add_row([item.name, item.version, item.arch, active, visible, releaseDate])
                                print table.draw() + "\n"
                                printer.out("Found " + str(nb) + " distribution(s).\n")
                        else:
                                printer.out("Subscription profile doesn't have any distribution.\n")
                        if subscription.targetFormats.targetFormat:
                                printer.out("Target Formats Details :")
                                table = Texttable(200)
                                table.set_cols_align(["l", "l"])
                                table.header(["Target Format", "Access"])
                                targetFormatsSorted = order_list_object_by(subscription.targetFormats.targetFormat, "name")

                                for item in targetFormatsSorted:
                                        if item.access:
                                                access = "X"
                                        else:
                                                access = ""
                                        table.add_row([item.name, access])
                                print table.draw() + "\n"
                                printer.out("Found " + str(nbFormat) + " target format(s).\n")
                        else:
                                printer.out("Subscription profile doesn't have any target formats.\n")
                        if subscription.targetPlatforms.targetPlatform:
                                printer.out("Target Platforms Details :")
                                table = Texttable(200)
                                table.set_cols_align(["l", "l"])
                                table.header(["Target Platform", "Access"])
                                targetPlatformsSorted = order_list_object_by(subscription.targetPlatforms.targetPlatform, "name")

                                for item in targetPlatformsSorted:
                                        if item.access:
                                                access = "X"
                                        else:
                                                access = ""
                                        table.add_row([item.name, access])
                                print table.draw() + "\n"
                                printer.out("Found " + str(nbPlatform) + " target platform(s).\n")
                        else:
                                printer.out("Subscription profile doesn't have any target platforms.\n")

                        printer.out("Quota Details :")
                        userQuotas = generics_utils.order_list_object_by(userQuotas.quotas.quota, "type")
                        quotas = generics_utils.order_list_object_by(subscription.quotas.quota, "type")
                        table = Texttable(200)
                        table.set_cols_align(["c", "c", "c"])
                        table.header(["Type", "Limit", "Frequency"])
                        for userQuota in userQuotas:
                                found = False
                                for item in quotas:
                                        if item.type == userQuota.type:
                                                found = True
                                                if item.frequency is None:
                                                        frequency = "-"
                                                else:
                                                        frequency = item.frequency
                                                if constants.QUOTAS_DISK_USAGE == item.type:
                                                        table.add_row([item.type, size(item.limit, system=alternative), frequency])
                                                else:
                                                        table.add_row([item.type, item.limit, frequency])
                                if not found:
                                        table.add_row([userQuota.type, "unlimited", "-"])
                        print table.draw() + "\n"

                        return 0

                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_info()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_info(self):
                doParser = self.arg_info()
                doParser.print_help()

        def arg_create(self):
                doParser = ArgumentParser(prog=self.cmd_name + " create", add_help=True, description="Create a new subscription profile within an organization.")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--name', dest='name', required=True, help="The name of the subscription profile to create")
                mandatory.add_argument('--code', dest='code', required=True, help="The code of the subscription profile to create")
                optional.add_argument('--description', dest='description', type=str, required=False, help="The description of the subscription profile to create")
                optional.add_argument('--active', dest='active', action='store_true', required=False, help="Flag to make the subscription profile active.")
                optional.add_argument('--admins', dest='admins', nargs='+', required=False, help="Admin users to be added to the subscription profile that can use the subscription profile to create a user (users separated by spaces)")
                optional.add_argument('--roles', dest='roles', nargs='+', required=False, help="Roles to be added to the subscription profile")
                optional.add_argument('--org', dest='org', required=False, help="The organization name. If no organization is provided, then the default organization is used.")
                return doParser

        def do_create(self, args):
                try:
                        # add arguments
                        doParser = self.arg_create()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)

                        # call UForge API
                        printer.out("Creating subscription profile [" + doArgs.name + "] ...")

                        # create a user manually
                        new_subscription_profile = subscriptionProfile()
                        new_subscription_profile.name = doArgs.name
                        new_subscription_profile.code = doArgs.code
                        if doArgs.description:
                                new_subscription_profile.description = doArgs.description
                        if doArgs.active:
                                new_subscription_profile.active = doArgs.active

                        new_subscription_profile.admins = pyxb.BIND()
                        if doArgs.admins:
                                for a in doArgs.admins:
                                        new_admin = userProfile()
                                        new_admin.loginName = a
                                        new_subscription_profile.admins.append(new_admin)

                        new_subscription_profile.roles = pyxb.BIND()
                        if doArgs.roles:
                                for a in doArgs.roles:
                                        new_role = role()
                                        new_role.name = a
                                        new_subscription_profile.roles.append(new_role)

                        # Send the create user request to the server
                        new_subscription_profile = self.api.Orgs(org.dbId).Subscriptions().Create(new_subscription_profile)

                        if new_subscription_profile is None:
                                printer.out("No information about the new subscription profile available", printer.ERROR)
                        else:
                                printer.out("New subscription profile [" + new_subscription_profile.name + "] created.", printer.OK)
                                table = Texttable(200)
                                table.set_cols_align(["c", "c", "c", "c"])
                                table.header(
                                        ["Name", "Code", "Active", "Description"])
                                table.add_row([new_subscription_profile.name, new_subscription_profile.code,
                                               "X" if new_subscription_profile.active else "", new_subscription_profile.description])
                                print table.draw() + "\n"
                        return 0

                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_create()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_create(self):
                doParser = self.arg_create()
                doParser.print_help()

        def arg_delete(self):
                doParser = ArgumentParser(prog=self.cmd_name + " delete", add_help=True, description="Delete a subscription profile from an organization.")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--name', dest='name', required=True, help="The name of the subscription profile to delete")
                optional.add_argument('--org', dest='org', required=False, help="The organization name. If no organization is provided, then the default organization is used.")
                return doParser

        def do_delete(self, args):
                try:
                        # add arguments
                        doParser = self.arg_delete()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        printer.out("Deleting subscription profile [" + doArgs.name + "] ...")
                        org = org_utils.org_get(self.api, doArgs.org)

                        # call UForge API
                        subscriptions = self.api.Orgs(org.dbId).Subscriptions().Getall(Search=None)

                        exist = False
                        for item in subscriptions.subscriptionProfiles.subscriptionProfile:
                                if item.name == doArgs.name:
                                        exist = True
                                        self.api.Orgs(org.dbId).Subscriptions(item.dbId).Remove(None)
                                        printer.out("Subscription profile [" + doArgs.name + "] deleted", printer.OK)
                                        break

                        if not exist:
                                printer.out("Subscription profile requested don't exist in [" + org.name + "]")
                                return 0
                        return 0

                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_delete()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_delete(self):
                doParser = self.arg_delete()
                doParser.print_help()

        def arg_update(self):
                doParser = ArgumentParser(prog=self.cmd_name + " update", add_help=True, description="Updates an existing subscription profile.")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--name', dest='name', required=True, help="The name of the subscription profile to update.")
                optional.add_argument('--description', dest='description', type=str, required=False, help="The description of the subscription profile to update.")
                optional.add_argument('--org', dest='org', required=False, help="The organization name. If no organization is provided, then the default organization is used.")
                return doParser

        def do_update(self, args):
                try:
                        doParser = self.arg_update()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        printer.out("Getting subscription profile with name [" + doArgs.name + "]...")
                        org = org_utils.org_get(self.api, doArgs.org)
                        subscriptions = self.api.Orgs(org.dbId).Subscriptions().Getall(Search=None)

                        exist = False
                        for item in subscriptions.subscriptionProfiles.subscriptionProfile:
                                if item.name == doArgs.name:
                                        exist = True
                                        updated_subscription = subscriptionProfile()
                                        updated_subscription.name = item.name
                                        updated_subscription.code = item.code
                                        updated_subscription.active = item.active
                                        if doArgs.description:
                                                updated_subscription.description = doArgs.description
                                        printer.out("Updating subscription profile with name [" + doArgs.name + "] ...")
                                        # call UForge API
                                        self.api.Orgs(org.dbId).Subscriptions(item.dbId).Update(updated_subscription)

                                        printer.out("Subscription profile [" + doArgs.name + "] updated.", printer.OK)

                        if not exist:
                                printer.out("Subscription profile requested don't exist in [" + org.name + "]")
                                return 0
                        return 0

                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_update()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_update(self):
                doParser = self.arg_update()
                doParser.print_help()

        def arg_enable(self):
                doParser = ArgumentParser(prog=self.cmd_name + " enable", add_help=True, description="Activates or enables a subscription profile within an organization.")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--name', dest='name', required=True, help="The name of the subscription profile to enable.")
                optional.add_argument('--org', dest='org', required=False, help="The organization name. If no organization is provided, then the default organization is used.")
                return doParser

        def do_enable(self, args):
                try:
                        # add arguments
                        doParser = self.arg_enable()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        printer.out("Getting subscription profile with name [" + doArgs.name + "]...")
                        org = org_utils.org_get(self.api, doArgs.org)
                        # call UForge API
                        subscriptions = self.api.Orgs(org.dbId).Subscriptions().Getall(Search=None)

                        exist = False
                        for item in subscriptions.subscriptionProfiles.subscriptionProfile:
                                if item.name == doArgs.name:
                                        exist = True
                                        updated_subscription = subscriptionProfile()
                                        updated_subscription.name = item.name
                                        updated_subscription.code = item.code
                                        if not item.active:
                                                updated_subscription.active = True
                                                printer.out("Enabling subscription profile with name [" + doArgs.name + "] ...")
                                                self.api.Orgs(org.dbId).Subscriptions(item.dbId).Update(updated_subscription)
                                                printer.out("Subscription [" + doArgs.name + "] is enabled.", printer.OK)
                                        else:
                                                printer.out("Subscription [" + doArgs.name + "] is already enabled", printer.WARNING)

                        if not exist:
                                printer.out("Subscription profile requested don't exist in [" + org.name + "]")
                                return 0
                        return 0

                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_enable()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_enable(self):
                doParser = self.arg_enable()
                doParser.print_help()

        def arg_disable(self):
                doParser = ArgumentParser(prog=self.cmd_name + " disable", add_help=True, description="Disables a subscription profile within an organization (cannot be used to reate users).")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--name', dest='name', required=True, help="The name of the subscription profile to update")
                optional.add_argument('--org', dest='org', required=False, help="The organization name. If no organization is provided, then the default organization is used.")
                return doParser

        def do_disable(self, args):
                try:
                        doParser = self.arg_enable()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        printer.out("Getting subscription profile with name [" + doArgs.name + "]...")
                        org = org_utils.org_get(self.api, doArgs.org)
                        subscriptions = self.api.Orgs(org.dbId).Subscriptions().Getall(Search=doArgs.name)

                        exist = False
                        for item in subscriptions.subscriptionProfiles.subscriptionProfile:
                                if item.name == doArgs.name:
                                        exist = True
                                        updated_subscription = subscriptionProfile()
                                        updated_subscription.name = item.name
                                        updated_subscription.code = item.code
                                        if item.active:
                                                updated_subscription.active = False
                                                printer.out("Disabling subscription profile with name [" + doArgs.name + "] ...")
                                                # call UForge API
                                                self.api.Orgs(org.dbId).Subscriptions(item.dbId).Update(updated_subscription)
                                                printer.out("Subscription [" + doArgs.name + "] is disabled.", printer.OK)
                                        else:
                                                printer.out("Subscription [" + doArgs.name + "] is already disabled", printer.WARNING)
                        if not exist:
                                printer.out("Subscription profile requested don't exist in [" + org.name + "]")
                                return 0
                        return 0

                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_enable()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_disable(self):
                doParser = self.arg_enable()
                doParser.print_help()
