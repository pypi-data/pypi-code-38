import onepanel
from onepanel.utilities.login_helper import login_helper
from onepanel.utilities.original_connection import Connection


from onepanel.sdk.jobs import Jobs
from onepanel.sdk.machine_types import MachineTypes
from onepanel.sdk.volume_types import VolumeTypes
from onepanel.sdk.environments import Environments

class Client():
    def __init__(self, username="", password="", token=""):
        conn = Connection()
        if username != "" and password != "" or token != "":
            data = login_helper(conn, "", username, password, token)
            if data is not None:
                conn.set_credentials(data['sessions'][0]['token'],data['account']['uid'])
        else:
            conn.load_credentials()

        self.jobs = Jobs(conn)
        self.machine_types = MachineTypes(conn)
        self.volume_types = VolumeTypes(conn)
        self.environments = Environments(conn)
