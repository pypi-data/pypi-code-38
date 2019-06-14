import json
import urllib.error
import urllib.parse
import urllib.request

from Homevee.Exception import DatabaseSaveFailedException, NoPermissionException
from Homevee.Item.User import User
from Homevee.Utils.Database import Database


class RemoteControlManager():
    def __init__(self):
        return

    def remote_control_enabled(self, db):
        REMOTE_CONTROL_ENABLED = db.get_server_data("USE_REMOTE_CONTROL", db)
        return REMOTE_CONTROL_ENABLED == "true"

    def set_remote_control_enabled(self, user: User, enabled, db: Database = None):
        if db is None:
            db = Database()
        if (not user.has_permission("admin")):
            return {'result': 'noadmin'}
        try:
            db.set_server_data("USE_REMOTE_CONTROL", enabled)
        except:
            raise DatabaseSaveFailedException

    def save_remote_data(self, user, remote_id, linked_account, db: Database = None):
        if db is None:
            db = Database()
        if (not user.has_permission("admin")):
            raise NoPermissionException

        try:
            db.set_server_data("REMOTE_ID", remote_id)
            db.set_server_data("REMOTE_LINKED_ACCOUNT", linked_account)
        except:
            raise DatabaseSaveFailedException

    def load_remote_data(self, user, db: Database = None):
        if db is None:
            db = Database()
        if (not user.has_permission("admin")):
            return {'result': 'noadmin'}

        remote_id = db.get_server_data("REMOTE_ID")
        access_token = db.get_server_data("REMOTE_ACCESS_TOKEN")
        linked_account = db.get_server_data("REMOTE_LINKED_ACCOUNT")

        # check if account is still linked

        # load premium membership
        url = "https://cloud.homevee.de/server-api.php?action=getpremiumuntil&remoteid=" + remote_id + "&accesstoken=" + access_token
        contents = urllib.request.urlopen(url).read()
        data = json.loads(contents)
        is_premium = None

        try:
            is_premium = data['is_premium']
            premium_until = data['premium_until']
        except:
            premium_until = None

        return {'remote_id': remote_id,
                'access_token': access_token,
                'linked_account': linked_account, 'premium_until': premium_until, 'is_premium': is_premium,
                'remote_control_enabled': self.remote_control_enabled(db)}

    def connect_remote_id_with_account(self, user, account_name, account_secret, db: Database = None):
        if db is None:
            db = Database()
        if (not user.has_permission("admin")):
            return {'result': 'noadmin'}


        remote_id = db.get_server_data("REMOTE_ID")
        url = "https://Homevee.de/connect-remote-id.php?remote_id=" + remote_id + "&account_name=" \
              + account_name + "&account_secret=" + account_secret
        response = urllib.request.urlopen(url).read()

        response = response.decode('utf-8')

        if response == "ok":
            db.set_server_data("REMOTE_LINKED_ACCOUNT", account_name)
            return True
        else:
            return False