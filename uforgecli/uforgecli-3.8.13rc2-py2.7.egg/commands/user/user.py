__author__="UShareSoft"

from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from ussclicore.cmd import Cmd, CoreGlobal
from texttable import Texttable
from user_admin import User_Admin_Cmd
from user_quota import User_Quota_Cmd
from user_os import User_Os_Cmd
from user_role import User_Role_Cmd
from user_api import User_Api_Cmd
from user_org import User_Org_Cmd
from user_targetPlatform import User_TargetPlatform_Cmd
from user_targetFormat import User_TargetFormat_Cmd
from ussclicore.utils import generics_utils, printer
from ussclicore.utils.generics_utils import order_list_object_by
from uforgecli.utils.uforgecli_utils import *
from uforgecli.utils import org_utils
from uforgecli.utils import constants
import random
import shlex


class User_Cmd(Cmd, CoreGlobal):
        """User's administration (list/info/create/update/delete etc)"""
    
        cmd_name="user"
    
        def __init__(self):
                self.generate_sub_commands()
                super(User_Cmd, self).__init__()

        def generate_sub_commands(self):
                if not hasattr(self, 'subCmds'):
                        self.subCmds = {}

                useradmin = User_Admin_Cmd()
                self.subCmds[useradmin.cmd_name] = useradmin

                userQuota = User_Quota_Cmd()
                self.subCmds[userQuota.cmd_name] = userQuota

                userOs = User_Os_Cmd()
                self.subCmds[userOs.cmd_name] = userOs

                userRole = User_Role_Cmd()
                self.subCmds[userRole.cmd_name] = userRole

                userApi = User_Api_Cmd()
                self.subCmds[userApi.cmd_name] = userApi

                userOrg = User_Org_Cmd()
                self.subCmds[userOrg.cmd_name] = userOrg

                userTargetPlatform = User_TargetPlatform_Cmd()
                self.subCmds[userTargetPlatform.cmd_name] = userTargetPlatform

                userTargetFormat = User_TargetFormat_Cmd()
                self.subCmds[userTargetFormat.cmd_name] = userTargetFormat

        def arg_list(self):
                doParser = ArgumentParser(prog=self.cmd_name+" list", add_help = True, description="List all the users in all the orgs. Only a root administrator can launch this command.")
                return doParser

        def do_list(self, args):
                try:
                        printer.out("Getting users list ...")
                        users = self.api.Users.Getall()
                        if users.users.user is None or len(users.users.user) == 0:
                                printer.out("There is no user.")
                        else:
                                users = order_list_object_by(users.users.user, "loginName")
                                printer.out("Users list :")
                                table = Texttable(200)
                                table.set_cols_align(["c", "c", "c", "c"])
                                table.header(["Id", "User", "Active", "Email"])
                                for item in users:
                                        if item.active:
                                                active = "X"
                                        else:
                                                active = ""
                                        table.add_row([item.dbId, item.loginName, active, item.email])
                                print table.draw() + "\n"

                                printer.out("Found " + str(len(users)) + " users.")
                        return 0
                except Exception as e:
                        handle_uforge_exception(e)

        def help_list(self):
                doParser = self.arg_list()
                doParser.print_help()

        def arg_enable(self):
                doParser = ArgumentParser(prog=self.cmd_name+" enable", add_help = True, description="Enable provided user")
                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--account', dest='account', required=True, help="User name of the account for which the current command should be executed")
                optional.add_argument('--resetPassword', dest='resetPassword', action='store_true', required=False, help="Reset the password of the enabled user.")

                return doParser

        def do_enable(self, args):
                try:
                        doParser = self.arg_enable()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        #call UForge API
                        printer.out("Enabling user ["+doArgs.account+"] ...")
                        user = self.api.Users(doArgs.account).Get()
                        if user is None:
                                printer.out("User "+ doArgs.account +" does not exist", printer.ERROR)
                        else:
                                if user.active:
                                        printer.out("User ["+doArgs.account+"] is already enabled", printer.WARNING)
                                else:
                                        user.active = True
                                        user = self.api.Users(doArgs.account).Update(body=user)
                                        printer.out("User ["+doArgs.account+"] is now enabled", printer.OK)

                                        #call reset password if option --resetPassword is specified
                                        if doArgs.resetPassword is not None and doArgs.resetPassword:
                                                printer.out("Resetting the password of user ["+user.loginName+"] ...")
                                                isReset = self.api.Users(doArgs.account).Forgotpassword.Reset(body=user)
                                                if isReset is not None:
                                                        printer.out("The password of user ["+user.loginName+"] has been correctly reset", printer.OK)

                                if user.active:
                                        actived = "X"
                                else:
                                        actived = ""
                                printer.out("Informations about ["+doArgs.account+"] :")
                                table = Texttable(200)
                                table.set_cols_align(["c", "l", "c", "c", "c", "c", "c", "c"])
                                table.header(["Login", "Email", "Lastname",  "Firstname",  "Created", "Active", "Promo Code", "Creation Code"])
                                table.add_row([user.loginName, user.email, user.surname , user.firstName, user.created.strftime("%Y-%m-%d %H:%M:%S"), actived, user.promoCode, user.creationCode])
                                print table.draw() + "\n"

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
                doParser = ArgumentParser(prog=self.cmd_name+" disable", add_help = True, description="Disable provided user")
                mandatory = doParser.add_argument_group("mandatory arguments")

                mandatory.add_argument('--account', dest='account', required=True, help="User name of the account for which the current command should be executed")
                return doParser

        def do_disable(self, args):
                try:
                        doParser = self.arg_disable()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        #call UForge API
                        printer.out("Disabling user ["+doArgs.account+"] ...")
                        user = self.api.Users(doArgs.account).Get()
                        if user is None:
                                printer.out("User "+ doArgs.account +" does not exist.", printer.ERROR)
                        else:
                                if not user.active:
                                        printer.out("User ["+doArgs.account+"] is already disabled", printer.WARNING)
                                else:
                                        user.active = False
                                        user = self.api.Users(doArgs.account).Update(body=user)
                                        printer.out("User ["+doArgs.account+"] is now disabled", printer.OK)

                                if user.active:
                                        actived = "X"
                                else:
                                        actived = ""
                                printer.out("Informations about ["+doArgs.account+"] :")
                                table = Texttable(200)
                                table.set_cols_align(["c", "l", "c", "c", "c", "c", "c", "c"])
                                table.header(["Login", "Email", "Lastname",  "Firstname",  "Created", "Active", "Promo Code", "Creation Code"])
                                table.add_row([user.loginName, user.email, user.surname , user.firstName, user.created.strftime("%Y-%m-%d %H:%M:%S"), actived, user.promoCode, user.creationCode])
                                print table.draw() + "\n"

                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_disable()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_disable(self):
                doParser = self.arg_disable()
                doParser.print_help()

        def arg_info(self):
                doParser = ArgumentParser(prog=self.cmd_name+" info", add_help = True, description="Get info on provided user")
                mandatory = doParser.add_argument_group("mandatory arguments")

                mandatory.add_argument('--account', dest='account', required=True, help="User name of the account for which the current command should be executed")
                return doParser

        def do_info(self, args):
                try:
                        doParser = self.arg_info()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2
                        
                        printer.out("Getting user ["+doArgs.account+"] ...")
                        user = self.api.Users(doArgs.account).Get()
                        if user is None:
                                printer.out("user "+ doArgs.account +" does not exist", printer.ERROR)
                        else:
                                if user.active:
                                        active = "X"
                                else:
                                        active = ""

                                printer.out("Informations about " + doArgs.account + ":",)
                                table = Texttable(200)
                                table.set_cols_align(["c", "l", "c", "c", "c", "c", "c", "c"])
                                table.header(["Login", "Email", "Lastname",  "Firstname",  "Created", "Active", "Promo Code", "Creation Code"])
                                table.add_row([user.loginName, user.email, user.surname , user.firstName, user.created.strftime("%Y-%m-%d %H:%M:%S"), active, user.promoCode, user.creationCode])
                                print table.draw() + "\n"
                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_info()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_info(self):
                doParser = self.arg_info()
                doParser.print_help()

        def arg_create(self):
                doParser = ArgumentParser(prog=self.cmd_name+" create", add_help = True, description="Create provided user")
                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--account', dest='account', required=True, help="User name of the account for which the current command should be executed")
                mandatory.add_argument('--code', dest='code', required=True, help="Subscription profile code to use for creating the permissions and quotas for the user.")
                mandatory.add_argument('--email', dest='email', required=True, help="Email of the account to create.")
                optional.add_argument('--accountPassword', dest='accountPassword', required=False, help="The new password to use for the account to create.  If this option is not provided, then a random eight letter password will be created for the new account.")
                optional.add_argument('--disable', dest='disable', action="store_true", required=False, help="Flag to de-activate the account during the creation")
                optional.add_argument('--org', dest='org', required=False, help="The organization name. If no organization is provided, then the default organization is used.")

                return doParser

        def do_create(self, args):
                try:
                        doParser = self.arg_create()
                        doArgs = doParser.parse_args(shlex.split(args))

                        #if the help command is called, parse_args returns None object
                        if not doArgs:
                                return 2

                        org = org_utils.org_get(self.api, doArgs.org)

                        newUser = user()
                        newUser.creationCode = doArgs.code
                        newUser.loginName = doArgs.account
                        newUser.email = doArgs.email
                        if doArgs.accountPassword is not None or doArgs.accountPassword == "":
                                newUser.password = doArgs.accountPassword
                                passwordSelection = False
                        else:
                                password = ""
                                for i in range(0,8,1):
                                        password += chr(random.randint(97,123))
                                newUser.password = password
                        if doArgs.disable:
                                newUser.active = False
                        else:
                                newUser.active = True

                        created = self.api.Users.Create(Org=org.name,Autopasswd=newUser.password,body=newUser,Notify=True,Notifyadmin=True)

                        table = Texttable(200)
                        table.set_cols_align(["c", "l", "c", "c", "c", "c", "c", "c"])
                        if created.active:
                                active = "X"
                        else:
                                active = ""
                        table.header(["Login", "Email", "Lastname",  "Firstname",  "Created", "Active", "Promo Code", "Creation Code"])
                        table.add_row([created.loginName, created.email, created.surname, created.firstName, created.created.strftime("%Y-%m-%d %H:%M:%S"), active, created.promoCode, created.creationCode])
                        print table.draw() + "\n"
                        printer.out("User \"" + created.loginName + "\" has been successfully created in [" + org.name + "].", printer.OK)
                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_create()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_create(self):
                doParser = self.arg_create()
                doParser.print_help()

