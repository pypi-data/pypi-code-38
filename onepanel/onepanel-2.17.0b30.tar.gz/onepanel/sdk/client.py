import onepanel
from onepanel.utilities.login_helper import login_helper
from onepanel.utilities.original_connection import Connection


from onepanel.sdk.jobs import Jobs
from onepanel.sdk.machine_types import MachineTypes
from onepanel.sdk.volume_types import VolumeTypes
from onepanel.sdk.environments import Environments

class Client():
    def __init__(self, email="", username="", access_token=""):
        conn = Connection()
        user_id_present = False
        if email != "":
            user_id_present = True
        if username != "":
            user_id_present = True

        user_cred_present = False
        if access_token != "":
            user_cred_present = True

        if user_id_present and user_cred_present:
            data = login_helper(conn, email, username, "", access_token)
            if data is not None:
                conn.set_credentials(data['sessions'][0]['token'],data['account']['uid'])
            self.jobs = Jobs(conn)
            self.machine_types = MachineTypes(conn)
            self.volume_types = VolumeTypes(conn)
            self.environments = Environments(conn)
            return
        if user_id_present or user_cred_present:
            print("Not enough identifying arguments present.")
            return
        else:
            conn.load_credentials()
            self.jobs = Jobs(conn)
            self.machine_types = MachineTypes(conn)
            self.volume_types = VolumeTypes(conn)
            self.environments = Environments(conn)
            return
