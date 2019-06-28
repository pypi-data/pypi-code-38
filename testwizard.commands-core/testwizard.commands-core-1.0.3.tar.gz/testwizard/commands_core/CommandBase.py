import urllib

class CommandBase():
    def __init__(self, session, testObjectName, name):
        if(session == None):
            raise Exception("Session is required")
        if(testObjectName == None):
            raise Exception("testObjectName is required")
        if(session.robot == None):
            raise Exception("robot is undefined for session")
        
        self.robot = session.robot
        self.session = session
        self.testObjectName = testObjectName

        self.url = "/api/v2/testruns/" + self.session.testRunId + "/testobjects/" + urllib.parse.quote(self.testObjectName) + "/commands/" + name
    
