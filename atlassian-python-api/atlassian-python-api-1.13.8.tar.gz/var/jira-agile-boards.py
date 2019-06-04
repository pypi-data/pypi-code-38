from atlassian import Jira
from var import config
import logging
import pprint

ATLASSIAN_USER = config.JIRA_LOGIN
ATLASSIAN_PASSWORD = config.JIRA_PASSWORD

logging.basicConfig(level=logging.ERROR)

jira = Jira(
    url=config.JIRA_URL,
    username=ATLASSIAN_USER,
    password=ATLASSIAN_PASSWORD)


pprint.pprint(jira.get_agile_card_colors(579))