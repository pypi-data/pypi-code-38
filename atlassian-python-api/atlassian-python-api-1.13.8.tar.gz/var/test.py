from atlassian import Jira
from atlassian import Stash
from var import config
from datetime import datetime
import logging
import pprint

ATLASSIAN_USER = config.JIRA_LOGIN
ATLASSIAN_PASSWORD = config.JIRA_PASSWORD

logging.basicConfig(level=logging.ERROR)

jira = Jira(
    url=config.JIRA_URL,
    username=ATLASSIAN_USER,
    password=ATLASSIAN_PASSWORD)

stash = Stash(
    url=config.STASH_URL,
    username=ATLASSIAN_USER,
    password=ATLASSIAN_PASSWORD
)
exclude_parameters = ['refs/heads/release/',
                      'refs/heads/master/',
                      'refs/heads/development/',
                      'refs/heads/develop/',
                      'refs/heads/afterpary/',
                      'refs/heads/ubfc/']

i = 0
pullrequests = []
flag = True


pprint.pprint()