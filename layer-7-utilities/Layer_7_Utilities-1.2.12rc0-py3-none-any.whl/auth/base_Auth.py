from ..database.database import oAuthDatabase
import praw


class BaseOAuth(object):
    def __init__(self, __description__, __version__, __author__, __botname__):
        self.USR_AGNT = __description__ + " v" + __version__ + " by " + __author__

    def login(self):
        r = praw.Reddit(user_agent=self.USR_AGNT,
                        client_id=self.APP_ID,
                        client_secret=self.APP_SECRET,
                        username=self.UNAME,
                        password=self.PASSWD)

        return r

    def set_info(self, id, secret, username, password):
        self.APP_ID, self.APP_SECRET, self.UNAME, self.PASSWD = id, secret, username, password


class oAuth(object):
    def __init__(self):
        self.db = None
        self.usernames = None
        self.accounts = None

    def get_accounts(self, id, __description__, __version__, __author__, __botname__, dbusername, dbpassword, dbhost, dbname):
        self.db = oAuthDatabase(dbusername, dbpassword, dbhost, dbname)
        self.usernames = self.db.get_accounts(id)

        self.accounts = []
        for i in self.usernames:
            x = BaseOAuth(__description__, __version__, __author__, __botname__)
            x.set_info(*i)
            self.accounts.append(x)
