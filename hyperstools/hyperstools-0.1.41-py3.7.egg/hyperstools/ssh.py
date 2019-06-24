# encoding: utf-8
import time
import paramiko
import re

from .lib import retry


@retry(mail=True)
def _getClient(**kwargs):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    hostname = kwargs.pop("hostname")
    kwargs.setdefault("port", "22")
    timeout = kwargs.pop('timeout', 3 * 60)
    client.connect(hostname, **kwargs, timeout=timeout)
    return client


class SSH(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.connect()


    def connect(self):
        self._client = _getClient(**self.kwargs)
        #channel = self._client.invoke_shell()
        #self.stdin = channel.makefile('wb')
        #self.stdout = channel.makefile('r')

    def exec(self, cmd):
        while True:
            try:
                stdin, stdout, stderr = self._client.exec_command(cmd)
                break
            except Exception:
                time.sleep(2)
                self._client.close()
                self.connect()
        stdout = stdout.read()
        stdout = str(stdout, encoding='utf8').split("\n")
        return stdin, stdout, stderr
    # def exec(self, cmd):
    #     """
    #
    #     :param cmd: the command to be executed on the remote computer
    #     :examples:  exec('ls')
    #                 exec('finger')
    #                 exec('cd folder_name')
    #     """
    #     cmd = cmd.strip('\n')
    #     self.stdin.write(cmd + '\n')
    #     finish = 'end of stdOUT buffer. finished with exit status'
    #     echo_cmd = 'echo {} $?'.format(finish)
    #     self.stdin.write(echo_cmd + '\n')
    #     shin = self.stdin
    #     self.stdin.flush()
    #
    #     shout = []
    #     sherr = []
    #     exit_status = 0
    #     for line in self.stdout:
    #         if str(line).startswith(cmd) or str(line).startswith(echo_cmd):
    #             # up for now filled with shell junk from stdin
    #             shout = []
    #         elif str(line).startswith(finish):
    #             # our finish command ends with the exit status
    #             exit_status = int(str(line).rsplit(maxsplit=1)[1])
    #             if exit_status:
    #                 # stderr is combined with stdout.
    #                 # thus, swap sherr with shout in a case of failure.
    #                 sherr = shout
    #                 shout = []
    #             break
    #         else:
    #             # get rid of 'coloring and formatting' special characters
    #             shout.append(re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]').sub('', line).
    #                          replace('\b', '').replace('\r', '').rstrip('\n'))
    #
    #     # first and last lines of shout/sherr contain a prompt
    #     if shout and echo_cmd in shout[-1]:
    #         shout.pop()
    #     if shout and cmd in shout[0]:
    #         shout.pop(0)
    #     if sherr and echo_cmd in sherr[-1]:
    #         sherr.pop()
    #     if sherr and cmd in sherr[0]:
    #         sherr.pop(0)
    #     if not shout or (len(shout) == 1 and not shout[0]):  # [] or [''] 则重连ssh
    #         self.connect()
    #     return shin, shout, sherr

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._client.close()
