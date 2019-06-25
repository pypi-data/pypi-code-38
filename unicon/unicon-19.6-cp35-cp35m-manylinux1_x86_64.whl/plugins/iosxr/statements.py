__copyright__ = "# Copyright (c) 2016 by cisco Systems, Inc. All rights reserved."
__author__ = "Syed Raza <syedraza@cisco.com>"

from unicon.plugins.generic.statements import GenericStatements
from unicon.plugins.iosxr.patterns import IOSXRPatterns
from unicon.eal.dialogs import Statement, Dialog
from unicon.eal.helpers import sendline

patterns = IOSXRPatterns()


class IOSXRStatements(GenericStatements):

    def __init__(self):
        super().__init__()
        self.secret_password_stmt = Statement(
            pattern=patterns.secret_password_prompt,
            action='sendline_ctx(tacacs_password)',
            args=None,
            loop_continue=True,
            continue_timer=False
        )
        self.commit_replace_stmt = Statement(
            pattern=patterns.commit_replace_prompt,
            action=sendline,
            args={'command': 'yes'},
            loop_continue=True,
            continue_timer=False
        )
        self.confirm_y_prompt_stmt = Statement(
            pattern=patterns.confirm_y_prompt,
            action=sendline,
            args={'command': 'y'},
            loop_continue=True,
            continue_timer=False
        )


iosxr_statements = IOSXRStatements()

authentication_statement_list = [
    iosxr_statements.bad_password_stmt,
    iosxr_statements.login_incorrect,
    iosxr_statements.login_stmt,
    iosxr_statements.useraccess_stmt,
    iosxr_statements.password_stmt,
    iosxr_statements.secret_password_stmt,
]
