from jira import JIRA
import dateutil.parser


class JIRA2:
    def __init__(self):
        self.instance = None

    def connect(self, jiraServerURL, username, password, verifyCertificate):
        options = {
            'server': jiraServerURL,
            'verify': verifyCertificate
        }

        auth = (username, password)

        self.instance = JIRA(options=options, auth=auth)

    def isConnected(self):
        return self.instance is not None

    def getUsers(self, byUsername, projectKeys):
        users = self.instance.search_assignable_users_for_issues(
            byUsername,
            projectKeys,
            expand=True,
            startAt=0,
            maxResults=1)
        return users

    def getIssueTypesForProject(self, projectKey):
        issueTypes = self.instance.issue_types()
        return issueTypes

    def getAllIssuesOnProject(self, projectKey, maxIssues):
        jql = 'project = {:s} ORDER BY created ASC'.format(projectKey)
        issues = self.instance.search_issues(jql, maxResults=maxIssues)
        return issues

    def getProjects(self):
        projects = []
        try:
            projects = self.instance.projects()
        except:
            pass
        return projects

    def getIssue(self, issueKey):
        issue = self.instance.issue(issueKey)
        return issue

    def createIssue(self, projectKey, user, summary, description, issueTypeName):
        fields = {
            'project': {'key': projectKey},
            'summary': summary,
            'description': description,
            'issuetype': {'name': issueTypeName}
        }
        # 'assignee': {'name': user.key},
        # 'reporter': {'name': user.key},

        issue = self.instance.create_issue(fields=fields)
        return issue

    def addWorkLog(self, jiraUser, jiraIssue, genericWorklog):
        timeSpentWithUnit = "{}s".format(genericWorklog.durationInSeconds)
        timeSpentWithoutUnit = genericWorklog.durationInSeconds
        started = dateutil.parser.parse(genericWorklog.date, ignoretz=True)
        instanceWorklog = self.instance.add_tasklog(jiraIssue,
                                                    timeSpentSeconds=timeSpentWithoutUnit,
                                                    adjustEstimate="auto",
                                                    reduceBy=timeSpentWithUnit,
                                                    started=started,
                                                    user=jiraUser.name,
                                                    comment=genericWorklog.description
                                                    )

        return instanceWorklog
