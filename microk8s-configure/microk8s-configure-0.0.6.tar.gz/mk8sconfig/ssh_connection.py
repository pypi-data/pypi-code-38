import paramiko


class SSHConnect:
    p = paramiko.SSHClient()
    p.load_system_host_keys()

    def __init__(self, user: str, password: str, address: str, port: int = 22):
        self.p.connect(address, port=port, username=user, password=password, )

    def exec(self, command: str) -> str:
        stdin, stdout, stderr = self.p.exec_command("shopt -s expand_aliases ; source ~/.bashrc; "+command)
        opt = str(stdout.read(), "utf-8")
        if len(opt) == 0:
            opt = str(stderr.read(), "utf-8")
        opt = "".join(opt)
        return opt