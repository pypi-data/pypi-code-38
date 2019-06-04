from atlassian import Bitbucket
import datetime
import config
import pprint
import logging

CONFLUENCE_URL = config.CONFLUENCE_URL
CONFLUENCE_LOGIN = config.CONFLUENCE_LOGIN
CONFLUENCE_PASSWORD = config.CONFLUENCE_PASSWORD
DRAFT_DAYS = 10

logging.basicConfig(level=logging.DEBUG)

stash = Bitbucket(url='https://stash.orcsoftware.com',
                  username=CONFLUENCE_LOGIN,
                  password=CONFLUENCE_PASSWORD)

pprint.pprint(stash.repo_all_list('PROEM'))