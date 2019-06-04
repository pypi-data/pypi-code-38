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


pprint.pprint(jira.user('cmt-fund-22'))

jira.remove_user_from_group('cmt-fund-22', 'external-users')

jira.get_all_users_from_group(include_inactive_users=True)