# Copyright (c) 2018-2019. Uniquid Inc. or its affiliates. All Rights Reserved.
#
# License is in the "LICENSE" file accompanying this file.
# See the License for the specific language governing permissions and limitations under the License.

import os
import paramiko
import scp
import socket

# constants
# SSH timeout in seconds
_timeout_secs = 60


def _is_error(in_text):
    """Checks if an error occurred when running a command.
        Arguments:
        in_text -- Text string.
        Returns: True if the word error was found, otherwise false.
    """
    retval = False
    if ('error' in in_text.casefold() or
            'command not found' in in_text.casefold()):
        retval = True
    return retval


def ssh_command(in_ip:str=None, in_port:str='22', in_user:str=None, in_pem_file:str=None, in_password:str=None, in_command:str=None):
    """
    Run a command on a remote machine and return the output in an dictionary.
    Either the path to a pem file or a text password must be specified.
    No text is written to the console by this function.
    Arguments:
      in_ip: IP address or Hostname of the remote machine.
      in_port: Port number for ssh. Defaults to 22.
      in_user: Linux user name.
      in_pem_file: Full path of PEM file (Optional)
      in_password: Text of the password (Optional)
      in_command: Command to run on remote machine.
    Returns:
    Dictionary containing the return code, stdout and stderr from a command.
    """
    assert in_ip is not None
    assert in_port is not None
    assert in_user is not None
    assert in_command is not None
    assert (in_pem_file is not None) or (in_password is not None)
    assert in_pem_file is not in_password
    retval = {
        'returncode': 0,
        'stdout': None,
        'stderr': None
    }
    client = None
    try:
        if (in_pem_file and
                not os.path.isfile(in_pem_file)):
            retval['returncode'] = 1
            retval['stderr'] = 'Error: Missing pem file: ' + in_pem_file
        elif in_pem_file:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=in_ip,
                           port=in_port,
                           username=in_user,
                           key_filename=in_pem_file,
                           allow_agent=False,
                           look_for_keys=False)
            stdin, stdout, stderr = client.exec_command(in_command,
                                                        timeout=_timeout_secs)
            stdin.close()
            retval['returncode'] = 0
            retval['stdout'] = stdout.read().decode('utf-8').strip()
            retval['stderr'] = stderr.read().decode('utf-8').strip()
            if _is_error(retval.get('stderr')):
                retval['returncode'] = 2
        elif in_password:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=in_ip,
                           port=in_port,
                           username=in_user,
                           password=in_password.strip())
            stdin, stdout, stderr = client.exec_command(in_command,
                                                        timeout=_timeout_secs)
            stdin.close()
            retval['returncode'] = 0
            retval['stdout'] = stdout.read().decode('utf-8').strip()
            retval['stderr'] = stderr.read().decode('utf-8').strip()
            if _is_error(retval.get('stderr')):
                retval['returncode'] = 3
    except paramiko.SSHException:
        retval['returncode'] = 4
        retval['stderr'] = 'Error: SSH connection returned an error.'
    except paramiko.AuthenticationException :
        retval['returncode'] = 5
        retval['stderr'] = 'Error: SSH authentication failed.'
    except paramiko.BadHostKeyException:
        retval['returncode'] = 6
        retval['stderr'] = 'Error: SSH bad host key error.'
    except socket.error:
        retval['returncode'] = 7
        retval['stderr'] = 'Error: SSH socket error occurred.'
    except TimeoutError:
        retval['returncode'] = 8
        retval['stderr'] = 'Error: SSH connection timed out.'
    finally:
        if client:
            client.close()
    return retval


def upload_file(in_ip:str=None,
                    in_port:str='22',
                    in_user:str=None,
                    in_pem_file:str=None,
                    in_password:str=None,
                    in_local_path:str=None,
                    in_remote_path:str=None):
    """
    Upload a file using the SCP protocol to a remote Linux server.
    Either the path to a pem file or a text password must be specified.
    Arguments:
      in_ip: IP address of the remote machine.
      in_port: Port number for ssh. Defaults to 22.
      in_user: Linux user name.
      in_pem_file: Full path of the PEM file (Optional)
      in_password: Text of the password (Optional)
      in_local_path: Local path to the file.
      in_remote_path: Path of new file on the remote server.
    Returns:
    Dictionary containing the return code, stdout and stderr from a command.
    """
    assert in_ip is not None
    assert in_port is not None
    assert in_user is not None
    assert (in_pem_file is not None) or (in_password is not None)
    assert in_pem_file is not in_password
    assert in_local_path != None
    assert in_remote_path != None
    retval = {
        'returncode': 0,
        'stdout': None,
        'stderr': None
    }
    sshClient = None
    scpClient = None
    try:
        if not os.path.isfile(in_local_path):
            retval['returncode'] = 1
            retval['stderr'] = 'Error: Cannot find local file: ' + in_local_path
        elif (in_pem_file and
                not os.path.isfile(in_pem_file)):
            retval['returncode'] = 2
            retval['stderr'] = 'Error: Missing pem file: ' + in_pem_file
        elif in_pem_file:
            sshClient = paramiko.SSHClient()
            sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshClient.connect(hostname=in_ip,
                           port=in_port,
                           username=in_user,
                           key_filename=in_pem_file,
                           allow_agent=False,
                           look_for_keys=False)
            scpClient = scp.SCPClient(sshClient.get_transport())
            scpClient.put(in_local_path, in_remote_path)
        elif in_password:
            sshClient = paramiko.SSHClient()
            sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshClient.connect(hostname=in_ip,
                           port=in_port,
                           username=in_user,
                           password=in_password.strip())
            scpClient = scp.SCPClient(sshClient.get_transport())
            scpClient.put(in_local_path, in_remote_path)
    except paramiko.SSHException:
        retval['returncode'] = 3
        retval['stderr'] = 'Error: SSH connection returned an error.'
    except paramiko.AuthenticationException :
        retval['returncode'] = 4
        retval['stderr'] = 'Error: SSH authentication failed.'
    except paramiko.BadHostKeyException:
        retval['returncode'] = 5
        retval['stderr'] = 'Error: SSH bad host key error.'
    except TimeoutError:
        retval['returncode'] = 6
        retval['stderr'] = 'Error: SSH connection timed out.'
    finally:
        if sshClient:
            sshClient.close()
        if scpClient:
            scpClient.close()
    return retval
