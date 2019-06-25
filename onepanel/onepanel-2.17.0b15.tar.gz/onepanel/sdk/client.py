from onepanel.utilities.original_connection import Connection

from onepanel.sdk.jobs import Jobs
from onepanel.sdk.machine_types import MachineTypes
from onepanel.sdk.volume_types import VolumeTypes
from onepanel.sdk.environments import Environments

class Client():
    def __init__(self, token=None, account_uid=None):
        conn = Connection()
        if account_uid and token:
            conn.set_credentials(token, account_uid)
        else:
            conn.load_credentials()

        self.jobs = Jobs(conn)
        self.machine_types = MachineTypes(conn)
        self.volume_types = VolumeTypes(conn)
        self.environments = Environments(conn)
