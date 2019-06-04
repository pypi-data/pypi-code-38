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
"""
while flag:
    result = stash.get_pull_requests("TB", 'tb', state='MERGED', order='oldest', limit=50, start=i * 50)
    if len(result) > 0:
        pullrequests.append(result)
        i = i + 1
    else:
        flag = False


while flag:
    pullrequests = stash.get_pull_requests("TB", 'tb', state='MERGED', order='oldest', limit=50, start=i * 50)
    if len(pullrequests) > 0:
        for pullrequest in pullrequests:
            if pullrequest.get('properties').get('openTaskCount') == 0:
                branch_id_name = pullrequest.get('fromRef').get('displayId')
                if any(x in branch_id_name for x in exclude_parameters):
                    continue
                if len(stash.get_branches("TB", 'tb', filter=branch_id_name)) > 0:
                    print(pullrequest)
        i = i + 1
    else:
        flag = False
"""

branches = stash.get_branches("TB", 'tb', start=0, limit=10, order_by='MODIFICATION')
for branch in branches:
    display_id = branch.get('displayId')
    branch_id_name = branch.get('id')
    if any(x in branch_id_name for x in exclude_parameters):
        continue
    if branch.get('isDefault'):
        continue
    latest_commit = branch.get('latestCommit')

    pprint.pprint(branch)
    """
    if len(stash.get_pull_requests_contain_commit("TB", 'tb', commit=latest_commit)) == 0:
        # branches without pull requests
        print(branch.get('displayId'))
        continue
    """
# print(stash.get_pullrequest("TB", 'tb', pull_request_Id="1"))

# 'https://stash.orcsoftware.com/rest/api/1.0/projects/{projectKey}/repos/{repositorySlug}/pull-requests'
