# coding: utf8
import config
from atlassian import Bitbucket
from pprint import pprint
import logging

logging.basicConfig(level=logging.ERROR)

""" Login part"""

confl = Bitbucket(
    url="https://stash.orcsoftware.com",
    username=config.ATLASSIAN_LOGIN,
    password=config.ATLASSIAN_PASSWORD)

confl.open_pull_request("INT", "jira-orc-crm-plugin", "INT", "jira-orc-crm-plugin",)