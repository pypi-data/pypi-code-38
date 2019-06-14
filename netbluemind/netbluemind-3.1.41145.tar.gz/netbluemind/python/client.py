from netbluemind.python import serder
import time
import sys

class BMClient:
    def __init__(self, baseUrl, apiKey = None):
        self.baseUrl = baseUrl
        self.apiKey = apiKey

    def instance(self, klass, *args):
        ccArgs = []
        ccArgs.append(self.apiKey)
        ccArgs.append(self.baseUrl)
        for a in args:
            ccArgs.append(a)

        return klass(*ccArgs)

    def login(self, login, password):
        from netbluemind.authentication.api.IAuthentication import IAuthentication
        auth = self.instance(IAuthentication)
        res = auth.login(login, password, "python")
        if( res.status.name == 'Bad'):
            raise ServerFault(None, None, "Bad login/pass")
        else:
            self.apiKey = res.authKey

    def domains(self):
        from netbluemind.domain.api.IDomains import IDomains
        return self.instance(IDomains)

    def directory(self, domain):
        from netbluemind.directory.api.IDirectory import IDirectory
        return self.instance(IDirectory, domain)

    def users(self, domain):
        from netbluemind.user.api.IUser import IUser
        return self.instance(IUser,domain)

    def groups(self, domain):
        from netbluemind.group.api.IGroup import IGroup
        return self.instance(IGroup,domain)

    def addressbook(self, uid):
        from netbluemind.addressbook.api.IAddressBook import IAddressBook
        return self.instance(IAddressBook,uid)

    def calendar(self, uid):
        from netbluemind.calendar.api.ICalendar import ICalendar
        return self.instance(ICalendar,uid)

    def mailboxes(self, domain):
        from netbluemind.mailbox.api.IMailboxes import IMailboxes
        return self.instance(IMailboxes, domain)

    def mailboxesMgmt(self, domain):
        from netbluemind.mailbox.api.IMailboxMgmt import IMailboxMgmt
        return self.instance(IMailboxMgmt, domain)

    def containerMgmt(self, containerUid):
        from netbluemind.core.container.api.IContainerManagement import IContainerManagement
        return self.instance(IContainerManagement, containerUid)

    def installation(self):
        from netbluemind.system.api.IInstallation import IInstallation
        return self.instance(IInstaltion)

    def servers(self, containerUid):
        from netbluemind.server.api.IServer import IServer
        return self.instance(IServer, containerUid)

    def domains(self):
        from netbluemind.domain.api.IDomains import IDomains
        return self.instance(IDomains)

    def domainSettings(self, domainUid):
        from netbluemind.domain.api.IDomainSettings import IDomainSettings
        return self.instance(IDomainSettings, domainUid)

    def userDevices(self, userUid):
        from netbluemind.device.api.IDevice import IDevice
        return self.instance(IDevice, userUid)

    def task(self, taskRef):
        from netbluemind.core.task.api.ITask import ITask
        return self.instance(ITask, taskRef.id)

    def jobs(self):
        from netbluemind.scheduledjob.api.IJob import IJob
        return self.instance(IJob)

    def waitTask(self, taskRef):
        from netbluemind.core.task.api.ITask import ITask
        from netbluemind.core.task.api.TaskStatusState import TaskStatusState
        task = self.instance(ITask, taskRef.id)
        status = task.status()
        while( status.state != TaskStatusState.InError and status.state != TaskStatusState.Success):
            time.sleep(0.1)
            status = task.status()
        return status

class BaseEndpoint:
    def handleResult__(self, sd, response):
        if ( "X-BM-WarnMessage" in response.headers):
            sys.stderr.write(response.headers["X-BM-WarnMessage"])

        if ( response.status_code == 204 ):
            return None
        elif( response.status_code <= 400 ):
            if( sd != None and serder.VOID != sd ):
                return sd.parse(response.json())
            else :
                return
        else:
            try:
                sf = response.json()
                raise ServerFault(sf.get("errorCode", 0),
                   sf.get("errorType", None),
                    sf.get("message", "unknown"))
            except ValueError:
                raise ServerFault(0, None, "unknown")

class ServerFault(Exception):
    def __init__(self, errorCode, errorType, message):
        super(ServerFault, self).__init__(errorCode, errorType, message)
