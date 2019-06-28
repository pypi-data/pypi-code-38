# coding: utf8
import config
from atlassian import Jira
from pprint import pprint

""" Login part"""

jira = Jira(
    url=config.JIRA_URL,
    username=config.ATLASSIAN_LOGIN,
    password=config.ATLASSIAN_PASSWORD)

custom_fieds = jira.get_all_projects()
print(custom_fieds)
for custom_fied in custom_fieds:
    print(custom_fied)