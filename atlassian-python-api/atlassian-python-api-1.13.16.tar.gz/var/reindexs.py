# coding: utf8
import config
from atlassian import Bitbucket
from pprint import pprint
import logging

logging.basicConfig(level=logging.INFO)

""" Login part"""

confl = Bitbucket(
    url=config.STASH_URL,
    username=config.ATLASSIAN_LOGIN,
    password=config.ATLASSIAN_PASSWORD)

confl.check_inbox_pull_requests()