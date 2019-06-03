import os
from sshtunnel import SSHTunnelForwarder
from bamboo_lib.connectors.models import BaseDriver


class SSHTunnelDriver(BaseDriver):
    '''
    Example Usage:
    sd = SSHTunnelDriver(host="canon-api.datausa.io", user="deploy", ssh_pkey="$HOME/.ssh/id_rsa_dw_deploy")
    sd.start()
    '''
    TYPE = 'Redis Connection Driver'

    def __init__(self, **kwargs):
        super(SSHTunnelDriver, self).__init__(**kwargs)
        host = kwargs.get("host", "localhost")
        local_port = kwargs.get("local_port", 6379)
        user = kwargs.get("user", "root")
        pw = kwargs.get("password", None)
        remote_port = kwargs.get("remote_port", 6379)
        ssh_pkey = kwargs.get("ssh_pkey", None)
        if ssh_pkey:
            ssh_pkey = os.path.expanduser(os.path.expandvars(ssh_pkey))
        ssh_private_key_password_env_var = kwargs.get("ssh_private_key_password_env_var", None)
        self.remote_server = SSHTunnelForwarder(
            host,
            ssh_username=user,
            ssh_password=pw,
            remote_bind_address=("127.0.0.1", remote_port),
            local_bind_address=("0.0.0.0", local_port),
            ssh_pkey=ssh_pkey,
            ssh_private_key_password=ssh_private_key_password_env_var
        )

    def start(self):
        return self.remote_server.start()

    def close(self):
        return self.remote_server.close()
