from atlassian import Jira
from var import config
import logging
import pprint

ATLASSIAN_USER = config.JIRA_LOGIN
ATLASSIAN_PASSWORD = config.JIRA_PASSWORD

logging.basicConfig(level=logging.ERROR)

jira = Jira(
    url="https://jirasandbox1.orcsoftware.com",
    username=ATLASSIAN_USER,
    password=ATLASSIAN_PASSWORD)


jira.create_or_update_issue_remote_links(issue_key='APP-18197', link_url='https://ya.ru', title='ya')