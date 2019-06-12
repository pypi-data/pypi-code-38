# encoding: utf-8

import re
import time
import socket
import logging_helper
from classutils.observer import Observable
from paramiko import SSHClient, AutoAddPolicy

logging = logging_helper.setup_logging()


class JumpBox(Observable):

    ANSI_ESCAPE = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')  # https://stackoverflow.com/a/14693789/2916546

    def __init__(self,
                 host,
                 username,
                 password,
                 elevated_username=None,
                 port=22,
                 log=False,
                 prompts=None):

        super(JumpBox, self).__init__()

        self.host = host
        self.username = username
        self.password = password
        self.elevated_user = elevated_username
        self.port = port
        self.log = log

        self.prompts = [u'~]$ ',
                        u'-bash-3.2$ '] + prompts if prompts is not None else []

        self.command_width = 80  # Set to default size when invoke_shell() is run!

        self.jumpbox_connected = False
        self.protected_host_connected = False
        self.protected_host_user = False

        logging_helper.getLogger(u"paramiko").setLevel(logging_helper.WARNING)

        self.connect()

    def connect(self):
        logging.info(u'Connecting to Jumpbox ({host}:{port}) as {user}'.format(host=self.host,
                                                                               port=self.port,
                                                                               user=self.username))

        self.ssh = SSHClient()
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())
        self.ssh.connect(hostname=self.host,
                         username=self.username,
                         password=self.password,
                         port=self.port,
                         timeout=120)

        self.shell = self.ssh.invoke_shell()
        self.transport = self.ssh.get_transport()
        self.transport.open_channel(kind="session")
        self.transport.set_keepalive(10)

        self.buffer = u''
        timeout = 120
        while not self.buffer.endswith(tuple(self.prompts)):
            if self.shell.recv_ready():
                self.buffer += self.shell.recv(1024)

            if not self.buffer.endswith(tuple(self.prompts)):
                if timeout == 0:
                    raise Exception(u'Timeout exceeded, terminating!')

                time.sleep(1)
                timeout -= 1

        resp = self.buffer.splitlines()
        if self.log:
            self.log_response(resp)

        if self.buffer.endswith(self.prompts[0]):

            self.jumpbox_connected = True
            logging.info(u'Connected to jumpbox ({host}:{port}) as {user}'.format(host=self.host,
                                                                                  port=self.port,
                                                                                  user=self.username))

            # TODO: make privilege elevation a method
            if self.elevated_user:
                resp, status = self.command(command=u'sudo su - {u}'.format(u=self.elevated_user))

                if resp[-1].endswith(self.prompts[1]):
                    logging.info(u'jumpbox privilege elevated to user: {u}'.format(u=self.elevated_user))

                else:
                    logging.error(u'Failed to elevate jump-box privilege to user: {u}'.format(u=self.elevated_user))

        else:
            logging.error(u'Failed to connect to jump-box!')

    def disconnect(self):

        logging.info(u'Disconnecting Jumpbox')

        self.ssh.close()

        self.jumpbox_connected = False
        self.protected_host_connected = False

        self.notify_observers(jumpbox=self)

        logging.info(u'Jumpbox Disconnected')

    def connect_to_protected_host(self,
                                  host,
                                  user=None,
                                  timeout=120,
                                  prompt=None):

        if prompt and prompt not in self.prompts:
            self.prompts.append(prompt)

        if self.jumpbox_connected:
            logging.info(u'Connecting to protected host {host}'.format(host=host))

            resp, status = self.command(command=u'ssh {h}'.format(h=host), timeout=timeout)

            if resp[-1].endswith(tuple(self.prompts)):
                self.protected_host_connected = True
                logging.info(u'Connected to protected host {host}'.format(host=host))

                if user:
                    logging.info(u'Authenticating as user {user}'.format(user=user))
                    user_resp, status = self.command(command=u'sudo su - {u}'.format(u=user), timeout=timeout)

                    if user_resp[-1].endswith(tuple(self.prompts)):
                        self.protected_host_user = True
                        logging.info(u'Authenticated as user {user}'.format(user=user))
                    else:
                        logging.error(u'Failed to elevate to {u} on {h}.'.format(u=user, h=host))

            else:
                logging.error(u'Failed to connect to protected host!')

        else:
            logging.error(u'Jump-box not connected!')

    def disconnect_protected_host(self):

        if self.protected_host_connected:
            logging.info(u'Disconnecting protected host')

            # TODO: Do we need to terminate any running commands here?

            # exit user elevation
            if self.protected_host_user:
                r, status = self.command(u'exit')

                if status:
                    self.protected_host_user = False
                    logging.info(u'Protected host User logged out')
                else:
                    logging.error(u'Failed to Exit protected host user elevation!')

            # Disconnect ssh session
            if not self.protected_host_user:
                r, status = self.command(u'exit')

                if status:
                    self.protected_host_connected = False
                    logging.info(u'Protected host Disconnected')
                else:
                    logging.error(u'Failed to disconnect from protected host!')

        else:
            logging.info(u'Protected host not connected!')

    @staticmethod
    def log_response(message):

        logging.info(u'================================================================================')

        for line in message:
            logging.info(line)

        logging.info(u'================================================================================')

    def command(self,
                command,
                timeout=60,
                expected_prompt=None):

        """
        Run Command on the connected jump-box session

        @param command: Command to be run
        @param expected_prompt: Last expected output
        @param timeout: Timeout before command should be terminated as unresponsive
        @return: response, status.
                 response: List of lines from command output. First line is the command, last line is the prompt.
                 status: True for success, False for failure
        """

        status = True

        try:

            if len(command) + 50 > self.command_width:
                logging.debug(u'Resizing pty!')
                self.command_width = len(command) + 50
                self.shell.resize_pty(width=self.command_width)  # Set width to avoid command overlapping lines
                self.shell.send(u'\n')
                self.__receive(timeout=timeout)

            if expected_prompt and expected_prompt not in self.prompts:
                self.prompts.append(expected_prompt)

            self.shell.send(command + u'\n')
            logging.debug(u'command sent ({c})...'.format(c=command))

            self.__receive(timeout=timeout)

            resp = self.buffer.splitlines()
            logging.debug(resp)

            # Remove command from response
            try:
                resp.remove(command)
                logging.debug(resp)

            except ValueError:
                pass

            if self.log:
                self.log_response(resp)

        except socket.error as err:
            logging.error(err)

            resp = None
            status = False

            self.disconnect()

        return resp, status

    def __strip_ansi(self):
        self.buffer = self.ANSI_ESCAPE.sub('', self.buffer)

    def __receive(self, timeout):

        TERMINATION_TIMEOUT = 10  # Arbitrary extra time for termination

        self.buffer = u''
        while not self.buffer.endswith(tuple(self.prompts)) and -TERMINATION_TIMEOUT < timeout:

            if timeout == 0:
                logging.warning(u'Timeout exceeded, terminating command!')
                self.shell.send("\x03")
                self.shell.send("\n")

                logging_helper.LogLines(log_lines="Received:"+self.buffer)
                logging_helper.LogLines(log_lines=["Expected prompt:"]+self.prompts)

            if self.shell.recv_ready():
                recv = self.shell.recv(1024)
                self.buffer = self.ANSI_ESCAPE.sub('', self.buffer + recv)
                logging_helper.LogLines(log_lines=recv,
                                        level=logging_helper.DEBUG)

            if self.buffer.endswith(u'Are you sure you want to continue connecting (yes/no)? '):
                self.command(command=u'yes')

            time.sleep(1)
            timeout -= 1

    def check_last_command_exit_status(self):

        """
        Check the exit status of the last command run

        Returns: True if both this command executed correctly & exit value = 0 otherwise its False
        """

        resp, status = self.command(command=u'echo $?')

        exit_status = True if int(resp[0]) == 0 else False

        return True if status and exit_status else False

    def curl(self,
             url,
             request_type=u'GET',
             headers=None,
             data=None,
             options=u''):

        logging.debug(url)
        logging.debug(request_type)
        logging.debug(headers)
        logging.debug(data)
        logging.debug(options)

        if self.protected_host_connected:
            # Compile headers if provided
            compiled_headers = u''
            if headers:
                for header in headers:
                    compiled_headers += u'-H "{key}: {value}" '.format(key=header,
                                                                       value=headers.get(header))

            logging.debug(compiled_headers)

            # Compile data if provided
            compiled_data = u"-d '{data}'".format(data=data) if data else u''

            # Build curl command
            command = u'curl {opts} -X {type} {headers} {data} "{url}"'.format(opts=options,
                                                                               type=request_type,
                                                                               headers=compiled_headers,
                                                                               data=compiled_data,
                                                                               url=url)

            logging.debug(command)

            response, status = self.command(command=command)

            logging.debug(response)
            logging.debug(status)

            response = u'\n'.join(response)
            logging.debug(response)

            if status:
                for prompt in self.prompts:
                    logging.debug(prompt)
                    if response.endswith(prompt):
                        logging.debug(u'Removing prompt')
                        response = response.replace(prompt, u'')

            curl_status = self.check_last_command_exit_status()

            return response, curl_status
