import onepanel
from onepanel.utilities.login_helper import login_helper
from onepanel.utilities.original_connection import Connection


from onepanel.sdk.jobs import Jobs
from onepanel.sdk.machine_types import MachineTypes
from onepanel.sdk.volume_types import VolumeTypes
from onepanel.sdk.environments import Environments

class Client():
    def __init__(self, email, username, password, token):
        conn = Connection()
        if email != "" or username != "" and password != "" or token != "":
            login_helper(conn, email, username, password, token)
            conn.load_credentials()
        else:
            conn.load_credentials()

        self.jobs = Jobs(conn)
        self.machine_types = MachineTypes(conn)
        self.volume_types = VolumeTypes(conn)
        self.environments = Environments(conn)
