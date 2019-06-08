from jira import JIRA


class Jira:
    def __init__(self, server: str, api_key: str, user: str):
        self._server = server
        self._api_key = api_key
        self._user = user

    @property
    def server(self):
        return self._server

    @property
    def api_key(self):
        return self._api_key

    @property
    def user(self):
        return self._user


    def get_issues(self, project: str):
        options = {
            'server': self.server
        }

        jira = JIRA(options, basic_auth=(self.user, self.api_key))

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