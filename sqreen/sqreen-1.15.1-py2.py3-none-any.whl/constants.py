# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Various constants
"""

LIFECYCLE_METHODS = {"PRE": "pre", "POST": "post", "FAILING": "failing"}

ACTIONS = {
    "RAISE": "raise",
    "ACTION_BLOCK": "action_block",
    "ACTION_REDIRECT": "action_redirect",
    "OVERRIDE": "override",
    "RETRY": "retry",
    "MODIFY_ARGS": "modify_args",
}


VALID_ACTIONS_PER_LIFECYCLE = {
    LIFECYCLE_METHODS["PRE"]: [
        ACTIONS["RAISE"],
        ACTIONS["ACTION_BLOCK"],
        ACTIONS["ACTION_REDIRECT"],
        ACTIONS["OVERRIDE"],
        ACTIONS["MODIFY_ARGS"],
    ],
    LIFECYCLE_METHODS["FAILING"]: [
        ACTIONS["RAISE"],
        ACTIONS["RETRY"],
        ACTIONS["OVERRIDE"],
    ],
    LIFECYCLE_METHODS["POST"]: [ACTIONS["RAISE"], ACTIONS["OVERRIDE"]],
}


BACKEND_URL = "https://back.sqreen.io"
CHANGELOG_URL = "https://docs.sqreen.io/sqreen-for-python/python-changelog/"
COMPATIBILITY_URL = (
    "https://docs.sqreen.io/sqreen-for-python/python-agent-compatibility/"
)
INSTALLATION_URL = (
    "https://docs.sqreen.io/sqreen-for-python/installing-the-python-agent/"
)
STATUS_URL = "http://status.sqreen.io/"
TERMS_URL = "https://www.sqreen.io/terms.html"
