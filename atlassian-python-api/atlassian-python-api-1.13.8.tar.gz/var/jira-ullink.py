# coding:utf-8

from atlassian import Jira
from var import config
import logging
import pprint

ATLASSIAN_USER = "gonchik.tsymzhitov"
ATLASSIAN_PASSWORD = config.CONFLUENCE_PASSWORD

logging.basicConfig(level=logging.ERROR)

jira = Jira(
    url="https://jira.orcsoftware.com",
    username=ATLASSIAN_USER,
    password=ATLASSIAN_PASSWORD)

query = 'project=SOATS  and "Display in release note" = Yes order by key'
issues = jira.jql(query)

for issue in issues.get('issues'):
    print("{} \t {}".format(issue.get('fields').get('customfield_104889'), issue.get('fields').get('customfield_104888')))




"""
filestore = open('text', 'r')

for line in filestore.readlines():
    params = line.split(';')
    print(params[1],params[2].strip(), params[3].strip())
    jira.user_update_email(params[1], params[3].strip())
"""