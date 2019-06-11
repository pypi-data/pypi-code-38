import random
import dateutil.parser


class MockJIRAUser:
    def __init__(self, name=None):
        self.name = name


class MockJIRAIssueType:
    def __init__(self, name=None, id=None):
        self.name = name
        self.id = id


class MockJIRAIssueFields:
    def __init__(self, summary=None, issueType=MockJIRAIssueType()):
        self.summary = summary
        self.issueType = issueType


class MockJIRAIssue:
    def __init__(self, key=None, fields=MockJIRAIssueFields()):
        self.id = random.randint(1, 100)
        self.key = key
        self.fields = fields


class MockJIRAProject:
    def __init__(self, key=None):
        self.key = key


class MockJIRAWorklog:
    def __init__(self, issueId=None, id=None, user=None, started=None, timeSpent=None, comment=None):
        self.issueId = issueId
        self.id = id
        self.author = user
        self.started = started
        self.timeSpent = timeSpent
        self.comment = comment


class MockJIRA:
    def __init__(self):
        self.DEFAULT_ISSUES = [
            MockJIRAIssue(key="MOCKTEST-1", fields=MockJIRAIssueFields(summary="Day 10")),
            MockJIRAIssue(key="MOCKTEST-3", fields=MockJIRAIssueFields(summary="Day 11")),
            MockJIRAIssue(key="MOCKTEST-4", fields=MockJIRAIssueFields(summary="Day 12 is a long day")),
            MockJIRAIssue(key="MOCKTEST-5", fields=MockJIRAIssueFields(summary="Not a day"))
        ]

    def connect(self, jiraServerURL, username, password, verifyCertificate):
        pass

    def isConnected(self, ):
        return True

    def getUsers(self, byUsername, projectKeys):
        users = [
            MockJIRAUser(name=byUsername),
            MockJIRAUser(name="Not me")
        ]
        return users

    def getIssueTypesForProject(self, projectKey):
        issueTypes = [
            MockJIRAIssueType(name="Bug", id=1),
            MockJIRAIssueType(name="Task", id=2)
        ]
        return issueTypes

    def getAllIssuesOnProject(self, projectKey, maxIssues):
        issues = self.DEFAULT_ISSUES
        return issues

    def getProjects(self):
        projects = [
            MockJIRAProject(key="MOCKTEST"),
            MockJIRAProject(key="MOCKPROJ")
        ]
        return projects

    def getIssue(self, issueKey):
        issue = next((issue for issue in self.DEFAULT_ISSUES if issue.key == issueKey), None)
        return issue

    def createIssue(self, projectKey, user, summary, description, issueTypeName):
        issueKey = "{} {}".format(projectKey, random.randint(1, 100))
        fields = MockJIRAIssueFields(summary=summary, issueType=MockJIRAIssueType(name=issueTypeName))
        issue = MockJIRAIssue(key=issueKey, fields=fields)

        return issue

    def addWorkLog(self, jiraUser, jiraIssue, genericWorklog):
        timeSpentWithUnit = "{}s".format(genericWorklog.durationInSeconds)
        started = dateutil.parser.parse(genericWorklog.date, ignoretz=True)
        return MockJIRAWorklog(issueId=jiraIssue.id, id=random.randint(100, 200), user=jiraUser, started=started,
                               timeSpent=timeSpentWithUnit, comment=genericWorklog.description)
