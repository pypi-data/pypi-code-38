#!/usr/bin/python3.6
from jira import JIRA


def get_issues(server: str, api_key: str, user: str, project: str):
    options = {
        'server': server
    }

    jira = JIRA(options, basic_auth=(user, api_key))

    jira_dashboards = jira.boards()

    board = [jira_dashboard for jira_dashboard in jira_dashboards if jira_dashboard.name == project]

    jra = jira.sprints(board[0].id)

    active = [sprint for sprint in jra if sprint.state == 'ACTIVE']

    sprint_info = jira.sprint(active[0].id)

    all_sprint_issues = jira.search_issues(f'project={project} and sprint = {sprint_info.id}')

    issues = []

    for issue in all_sprint_issues:
        if str(issue.fields.issuetype) != 'Technical Task':
            issues.append(
                {
                    'key': issue.key,
                    'type': str(issue.fields.issuetype),
                    'status': str(issue.fields.status),
                    'summary': issue.fields.summary
                }
            )

    return issues