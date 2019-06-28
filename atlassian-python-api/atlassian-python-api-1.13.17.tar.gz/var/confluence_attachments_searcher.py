# coding: utf8
import config
from atlassian import Confluence
from pprint import pprint
import logging

logging.basicConfig(level=logging.ERROR)

""" Login part"""

confl = Confluence(
    url=config.CONF_URL,
    username=config.ATLASSIAN_LOGIN,
    password=config.ATLASSIAN_PASSWORD)

pprint(confl.get_attachments_from_content(168002133))