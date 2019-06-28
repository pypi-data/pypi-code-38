import json
import urllib

class TestObjectBase():
    def __init__(self, session, name, category):
        if(session == None):
            raise Exception("Session is required")
        if(name == None):
            raise Exception("Name is required")
        if(category == None):
            raise Exception("Category is required")
        if(session.robot == None):
            raise Exception("Robot is undefined for session")

        resources = session.robot.metadata["resources"]
        for resource1 in resources:
            if(resource1["name"] == name):
                resource = resource1
                break
            else:
                resource = None
        if(resource == None):
            raise Exception("No resource found with name " + name)
        
        jsonData = session.robot.get("/api/v2/testobjects/" + urllib.parse.quote(resource["id"]), "Get TestObject by id failed")
        testobject = json.loads(jsonData.read().decode('utf-8'))
        for prop in testobject:
            if(prop in testobject):
                setattr(self, prop, testobject[prop])

        self.session = session
        self.name = name
        self.robot = session.robot
        self.baseUrl = "/api/v2/testruns/" + self.session.testRunId + "/testobjects/" + urllib.parse.quote(name) + "/commands/"
        self.disposed = False

    def checkIsDisposed(self):
        if(self.disposed):
            raise Exception("Cannot access a disposed object.")

    def dispose(self):
        self.disposed = True