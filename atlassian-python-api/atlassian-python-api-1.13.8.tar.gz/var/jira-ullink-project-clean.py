# coding:utf-8

from atlassian import Jira
from var import config
import logging
import pprint

ATLASSIAN_USER = config.CONFLUENCE_LOGIN
ATLASSIAN_PASSWORD = config.CONFLUENCE_PASSWORD

logging.basicConfig(level=logging.ERROR)

jira = Jira(
    url="http://jira-uat.ullink.lan",
    username=ATLASSIAN_USER,
    password=ATLASSIAN_PASSWORD)

jira_orc = Jira(
    url="https://jirasandbox1.orcsoftware.com",
    username=ATLASSIAN_USER,
    password=ATLASSIAN_PASSWORD)

ul_groups = jira.get_groups(limit=1000).get('groups')
for group_name in ul_groups:
    group_name = group_name['name']
    print(jira.get_all_users_from_group(group=group_name, limit=1000))
    # print(jira_orc.create_group()
