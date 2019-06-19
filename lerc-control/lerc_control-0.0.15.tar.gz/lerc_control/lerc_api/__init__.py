
import os
import sys
import time
import json
import logging
import requests
from hashlib import md5
from datetime import datetime
from contextlib import closing
from configparser import ConfigParser

# Get the working lerc_control directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def check_config(config, required_keys):
    """Just make sure the keys show up somewhere in the config - Not a fool-proof check

    :param ConfigParser config: A configparser.ConfigParser
    :param list required_keys: A list of required config keys
    :return: False if a key is missing, else config
    """
    logger = logging.getLogger(__name__+".check_config")
    at_least_one_missing = False
    if isinstance(required_keys, list) and required_keys:
        for key in required_keys:
            found = False
            for section in config.sections():
                if config.has_option(section, key):
                    found = True
                    break
            if not found:
                at_least_one_missing = True
                logger.error("Missing required config item: {}".format(key))
    if at_least_one_missing:
        return False
    return config


def load_config(profile='default', required_keys=[]):
    """Load lerc configuration. Configuration files are looked for in the following locations::
        /<python-lib-where-lerc_control-installed>/etc/lerc.ini
        /etc/lerc_control/lerc.ini
        /opt/lerc/lerc_control/etc/lerc.ini
        ~/<current-user>/.lerc_control/lerc.ini

    Configuration items found in later config files take presendence over earlier ones.

    :param str profile: (optional) Specifiy a group or company to work with.
    :param list required_keys: (optional) A list of required config keys to check for
    """
    logger = logging.getLogger(__name__+".load_config")
    config = ConfigParser()
    config_paths = []
    # default
    config_paths.append(os.path.join(BASE_DIR, 'etc', 'lerc.ini'))
    # global
    config_paths.append('/etc/lerc_control/lerc.ini')
    # legacy
    config_paths.append('/opt/lerc/lerc_control/etc/lerc.ini')
    # user specific
    config_paths.append(os.path.join(os.path.expanduser("~"),'.lerc_control','lerc.ini'))
    finds = []
    for cp in config_paths:
        if os.path.exists(cp):
            logger.debug("Found config file at {}.".format(cp))
            finds.append(cp)
    if not finds:
        logger.critical("Didn't find any config files defined at these paths: {}".format(config_paths))
        raise Exception("MissingLercConfig", "Config paths : {}".format(config_paths))

    config.read(finds)
    try:
        config[profile]
    except KeyError:
        logger.critical("No section named '{}' in configuration files : {}".format(profile, config_paths))
        raise

    if required_keys:
        check_config(config, required_keys)

    return config


######################
## lerc_api GLOBALS ##
######################
CONFIG = load_config()
QUERY_FIELDS = ['cmd_id', 'hostname', 'operation', 'cmd_status', 'client_id', 'client_status', 'version', 'company_id', 'company']
QUERY_FIELD_DICT = {'cmd_id': 'The ID of a specific command',
                    'hostname': 'The hostname of a client',
                    'operation': 'A Command operation type: upload,run,download,quit',
                    'cmd_status': 'The status of a command: pending,preparing,complete,error,unknown,started',
                    'client_id': 'Specify a LERC by ID',
                    'client_status': 'A LERC status: busy,online,offline,unknown,uninstalled',
                    'version': 'The LERC version string',
                    'company_id': 'Specify a company/group ID',
                    'company': 'A company/group name'}
QUERY_FIELD_DESCRIPTIONS = []
for key,value in QUERY_FIELD_DICT.items():
    QUERY_FIELD_DESCRIPTIONS.append({'field': key, 'description': QUERY_FIELD_DICT[key]})

def parse_lerc_server_query(query_str):
    """This function converts a string from field:value pairs into \*\*args that lerc_session.query can recognize.

    :param str query_str: A query string to be parsed.
    :return: \*\*args ready for lerc_session.Query()
    """
    logger = logging.getLogger(__name__+".parse_lerc_server_query")
    query_parts = query_str.split()
    args = {}
    negated_with_not = False
    for part in query_parts:
        negated = False
        if part[0] == '-' or part[0] == '!':
            negated = True
            part = part[1:]
        elif part.upper() == 'NOT':
            negated_with_not = True
            continue
        if negated_with_not:
            negated = True
            negated_with_not = False
        field = part[:part.find(':')]
        if field not in QUERY_FIELDS:
            logger.critical("{} is not a valid query filed. Valid fields: {}".format(field, QUERY_FIELDS))
            return False
        value = part[part.find(':')+1:]
        if negated:
            value = '-' + value
        args[field] = value
    return args


class Client():
    """Represents a Live Endpoint Response Client and is used to interact with this LERC.

    :param dict host_dict: A dictionary representaion of a LERC
    """

    contained = False
    logger = logging.getLogger(__name__+".Client")

    def __init__(self, host_dict, profile='default'):
        self.hostname = host_dict['hostname']
        self.version = host_dict['version']
        self.company_id = host_dict['company_id']
        self.id = host_dict['id']
        self.status = host_dict['status']
        self.sleep_cycle = host_dict['sleep_cycle']
        self.last_activity = host_dict['last_activity']
        self.install_date = host_dict['install_date']
        self._raw = host_dict
        self.profile = profile
        self._lerc_session = lerc_session(profile=profile)

    @property
    def get_dict(self):
        """Return the client as it's dictionary representation."""
        return self._raw

    def refresh(self):
        """Query the LERC Server to get an update on this LERC."""
        r = requests.get(self._ls.server+'/query', params={'client_id': self.id}, cert=self._ls.cert).json()
        if 'error' in r:
            self.logger.error("{}".format(r['error']))
            return False
        if 'clients' in r and len(r['clients']) == 1:
            r = r['clients'][0]
        else:
            self.logger.error("Unexpected result from server : {}".format(r))
            return False
        self.status = r['status']
        self.last_activity = r['last_activity']
        self.sleep_cycle = r['sleep_cycle']
        self.version = r['version']
        self.install_date = r['install_date']
        self._raw = r
        return True

    @property
    def is_online(self):
        """Return True if the client is Online."""
        self.refresh() 
        if self.status == 'ONLINE':
            return True
        return False

    @property
    def is_busy(self):
        """Return True is the client is Busy working on a command."""
        self.refresh()
        if self.status == 'BUSY':
            return True
        return False

    @property
    def _ls(self):
        """The Client's lerc_session object."""
        return self._lerc_session

    def __str__(self):
        text = "\n"
        text += "\tClient ID: {}\n".format(self.id)
        text += "\tHostname: {}\n".format(self.hostname)
        text += "\tStatus: {}\n".format(self.status)
        text += "\tCompany ID: {}\n".format(self.company_id)
        config = self._ls.get_config
        for section in config.sections():
            if config.has_option(section, 'company_id'):
                if config[section].getint('company_id') == int(self.company_id):
                    text += "\tCompany Name: {}\n".format(section)
        text += "\tVersion: {}\n".format(self.version)
        text += "\tSleep Cycle: {} seconds\n".format(self.sleep_cycle)
        text += "\tInstall Date: {}\n".format(self.install_date)
        text += "\tLast Activity: {}\n\n".format(self.last_activity)
        return text

    def _issue_command(self, command):
        # check the host, make the post
        arguments = {'host': self.hostname, 'id': self.id}
        headers={"content-type": "application/json"}
        r = requests.post(self._ls.server+'/command', cert=self._ls.cert, headers=headers,
                                                params=arguments, data=json.dumps(command))
        if r.status_code != requests.codes.ok:
            self.error = { 'status_code': r.status_code, 'message': "ERROR : {}".format(r.text) }
            self.logger.critical("Got status code '{}' : {}".format(r.status_code, r.json()['message']))
            raise Exception("Something went wrong with the server. Got '{}' response.".format(r.status_code)) from None
        else: # record the command
            result = r.json()
            if 'command' in result:
                self.logger.info("{} (CID: {})".format(result['message'], result['command']['command_id']))
                return Command(result['command'], profile=self.profile)
            else:
                if 'error' not in result:
                    raise Exception("Unexpected result: {}".format(result))
                self.logger.error("{}".format(results['error']))
                return False


    def Run(self, shell_command, async=False):
        """Execute a shell command on the host.

        :param str shell_command: The command to run on the host
        :param bool async: (optional) ``False``: LERC client will stream any results and  wait until for completion. ``True``: Execute the command and return immediately.
        """
        command = { "operation":"run", "command": shell_command, "async": async }
        return self._issue_command(command)

    def Download(self, server_file_path, client_file_path=None, analyst_file_path=None):
        """Instruct a client to download a file. The file will be streamed to the server if the server doesn't have it yet. The streamed to the client.

        :param str server_file_path: The path to the file that you want the client to download. If the supplied argument is the path to the file on the system this function is called, an attempt will be made to complete the analyst_file_path automatically.
        :param str client_file_path: (optional) where the client should write the file, defaults server config default directory + the file name taken off of the server_file_path.
        :param str analyst_file_path: (optional) path to the original file the analyst - This allows an analyst to resume a transfer between a lerc_session and the server. Neccessary for streaming the file to the server, if the server does not already have it
        """
        if analyst_file_path is None:
            analyst_file_path = server_file_path

        if '/' in server_file_path:
            server_file_path = server_file_path[server_file_path.rfind('/')+1:]

        command = { "operation":"download", "server_file_path":server_file_path,
                    "client_file_path":client_file_path, "analyst_file_path":analyst_file_path}

        command = self._issue_command(command)
        command.stream_file(analyst_file_path)
        return command

    def Upload(self, path):
        """Upload a file from client to server. The file will be streamed to the server and then streamed to the lerc_session.

        :param str path: The path to the file, on the endpoint
        """
        command = { "operation":"upload", "client_file_path":path }
        return self._issue_command(command)

    def Quit(self):
        """The Quit command tells the LERC client to uninstall itself from the endpoint.
        """
        command = { "operation":"quit" }
        return self._issue_command(command)

    def list_directory(self, dir_path):
        """List the given directory, read the results into a list and return the list.
        """
        command = self.Run('cd "{}" && dir'.format(dir_path))
        command.wait_for_completion()
        results = command.get_results(return_content=True)
        dir_lines = results.decode('utf-8').splitlines()
        results = {}
        results['dir_lines'] = dir_lines
        contents = []
        for line in dir_lines:
            content = {}
            if line:
                if line[2] == '/':
                    content['name'] = line[line.rfind(' ')+1:]
                    if 'DIR' in line:
                        content['type'] = 'DIR'
                        content['size'] = ''
                    else:
                        content['type'] = 'file'
                        line_no_name = line[:line.rfind(' ')]
                        content['size'] = line_no_name[line_no_name.rfind(' ')+1:]
                    contents.append(content)
                elif 'bytes' in line:
                    if 'File' in line:
                        line = line[:line.rfind(' ')]
                        dir_size = line[line.rfind(' ')+1:]
                        results['dir_size'] = dir_size
                    elif 'Dir' in line:
                        line = line[:line.rfind(' ')]
                        line = line[:line.rfind(' ')]
                        drive_free_space = line[line.rfind(' ')+1:]
                        results['drive_free_space'] = drive_free_space 

        results['dir_dict'] = contents
        return results

    def contain(self):
        """Use the windows firewall to isolate a host. Everything will be blocked but lerc's access outbound. You must attach to a host before using contain.
        This is implemented by dropping a bat file (a default is included in the lerc_control/tools dir) that will isolate a host with the windows firewall and only allow the lerc.exe client access through the firewall. The bat file will pause for ~60 seconds without prompting the user. Lerc is issued a run command to kill the bat file. If Lerc is able to fetch this run command from the control server, the bat file will be killed before the 60 seconds are up. If not, the bat file will undo all firewall changes.

        :return: True on success
        """

        if self.contained:
            return self.contained

        self.logger.info("containing host..")
        self.refresh()

        safe_contain_bat_path = self._ls.config[self._ls.profile]['containment_bat'] if self._ls.config.has_option(self._ls.profile,'containment_bat') else self._ls.config['default']['containment_bat']
        contain_cmd = self._ls.config[self._ls.profile]['contain_cmd'] if self._ls.config.has_option(self._ls.profile, 'contain_cmd') else self._ls.config['default']['contain_cmd']

        if not os.path.exists(safe_contain_bat_path):
            safe_contain_bat_path = os.path.join(BASE_DIR, safe_contain_bat_path)
            if not os.path.exists(safe_contain_bat_path):
                self.logger.error("Containment batch file '{}' does not exist.".format(safe_contain_bat_path))
                return False

        self.Download(safe_contain_bat_path)
        containment_command = self.Run(contain_cmd.format(int(self.sleep_cycle)+5), async=True)

        # Dummy command to give the containment command enough time to execute before lerc kills it with wmic
        self.Run("dir")

        bat_name = safe_contain_bat_path[safe_contain_bat_path.rfind('/')+1:]
        kill_command = self.Run('wmic process where "CommandLine Like \'%{}%\'" Call Terminate'.format(bat_name))

        # for spot checking
        check_command = self.Run('netsh advfirewall show allprofiles')

        if not containment_command.wait_for_completion():
            self.logger.error("Containment command failed : {}".format(containment_command))
            return False
        self.logger.debug("{}".format(containment_command))
        self.logger.info("Host contained at: {}".format(datetime.now()))

        self.logger.info("Command {} should return before {} seconds have passed.".format(kill_command.id, self.sleep_cycle))
        if not kill_command.wait_for_completion():
            self.logger.error("Waiting for kill command failed: {}".format(kill_command))
            return False
        self.logger.debug("{}".format(kill_command))

        self.logger.info("Getting firewall status for due diligence..")
        check_command.wait_for_completion()
        #check_command.get_results(file_path = "{}_{}_firewall_status.txt".format(self.hostname, check_command.id), print_run=False)
        results = check_command.get_results(return_content=True)
        if not results:
            self.logger.error("Problem getting firewall status.")
            return False
        results = results.decode('utf-8')
        if 'AllowOutbound' in results:
            self.logger.warn("AllowOutbound found in firewall status. Containment failed! : Firewall Status:\n{}".format(results))
            return False
        self.contained = True
        return self.contained

    # Move to Client class
    def release_containment(self):
        """Release containment on client.

        :return: True on success.
        """
        reset_cmd = self.Run("netsh advfirewall reset && netsh advfirewall show allprofiles")
        reset_cmd.wait_for_completion()
        self.logger.info("Host containment removed at: {}".format(datetime.now()))
        self.logger.info("Getting firewall status for due diligence..")
        reset_cmd.get_results(file_path = "{}_{}_firewall_reset.txt".format(self.hostname, reset_cmd.id), print_run=False)
        self.contained = False
        return not self.contained




class Command():
    """Represents a Live Endpoint Response Client Command.

    :param dict cmd_dict: A dictionary representation of a LERC Command.
    """

    logger = logging.getLogger(__name__+".Command")

    def __init__(self, cmd_dict, profile='default'):
        self.id = cmd_dict['command_id']
        self.hostname = cmd_dict['hostname']
        self.client_id = cmd_dict['client_id']
        self.operation = cmd_dict['operation']
        self.command = cmd_dict['command']
        self.status = cmd_dict['status']
        self.client_file_path = cmd_dict['client_file_path']
        self.server_file_path = cmd_dict['server_file_path']
        self.analyst_file_path = cmd_dict['analyst_file_path']
        self.async_run = cmd_dict['async_run']
        self.file_position = cmd_dict['file_position']
        self.filesize = cmd_dict['filesize']
        self._lerc_session = lerc_session(profile=profile)
        self._raw = cmd_dict

    def __str__(self):
        text = "\n\t----------------------------\n"
        text += "\tCommand ID: {}\n".format(self.id)
        text += "\tClient ID: {}\n".format(self.client_id)
        text += "\tHostname: {}\n".format(self.hostname)
        text += "\tOperation: {}\n".format(self.operation)
        if self.operation == 'RUN':
            text += "\t  |-> Command: {}\n".format(self.command)
            text += "\t  |-> Async: {}\n".format(self.async_run)
        text += "\tStatus: {}\n".format(self.status)
        text += "\tClient Filepath: {}\n".format(self.client_file_path)
        text += "\tServer Filepath: {}\n".format(self.server_file_path)
        text += "\tAnalyst Filepath: {}\n".format(self.analyst_file_path)
        text += "\tFile Position: {}\n".format(self.file_position)
        text += "\tFile Size: {}\n\n".format(self.filesize)
        return text

    @property
    def _ls(self):
        return self._lerc_session

    @property
    def get_dict(self):
        return self._raw

    def refresh(self, cmd_dict=None):
        """Query the lerc server and update this command with the latest data."""
        if not cmd_dict:
            r = requests.get(self._ls.server+'/query', cert=self._ls.cert, params={'cmd_id': self.id, 'rc': True}).json()
            if 'commands' in r and len(r['commands']) == 1:
                cmd_dict = r['commands'][0]
            else:
                self.logger.warning("No command by id:{}".format(self.id))
                return False
        self.status = cmd_dict['status']
        self.file_position = cmd_dict['file_position']
        self.filesize = cmd_dict['filesize']
        self.server_file_path = cmd_dict['server_file_path']

    def stream_file(self, file_path, position=0):
        """Stream a file to the lerc server that the server needs to for this command."""
        # file_path - file to send
        # position - position in file to send from (resume capable)
        if not os.path.exists(file_path):
            self.logger.error("{} does not exists. Aborting.".format(file_path))
            return False

        # get md5 of file
        md5_hasher = md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                md5_hasher.update(chunk)
        file_md5 = md5_hasher.hexdigest().lower()

        statinfo = os.stat(file_path)
        arguments = {'host': self.hostname, 'cid': self.id, 'filesize': statinfo.st_size, 'md5': file_md5}
        def gen():
            with open(file_path, 'rb') as f:
                f.seek(position)
                data = f.read(4096)
                while data:
                    yield data
                    data = f.read(4096)
        r = requests.post(self._ls.server+'/command/upload', cert=self._ls.cert, params=arguments, data=gen()).json()
        if 'error' in r:
            self.logger.error("{}".format(r['error']))
            return r
        if 'warn' in r:
            self.logger.info(r['warn'])
        self.refresh(cmd_dict=r)
        return True

    def get_error_report(self):
        """If an error report exists for this command, get it.
        """
        arguments = {'cid': self.id, 'error': True}
        r = requests.get(self._ls.server+'/command/download', cert=self._ls.cert, params=arguments).json()
        return r


    def get_results(self, file_path=None, chunk_size=None, print_run=True, return_content=False, position=0):
        """Get any results available for a command. If cid is None, any cid currently assigned to the lerc_session will be used.

        :param int cid: (optional) The Id of a command to work with.
        :param str file_path: (optional) The path to write the results. default: <hostname>_<cid>_filename to current dir.
        :param int chunk_size: (optional) Specify the size of the chunks (bytes) to stream with the server
        :param boolean print_run: (optionl default:True) If True, print Run command results to console
        :param boolean return_content: (content) Do not write the results to a file, return the results as a byte string
        :param int position: (optional) For manually specifing byte position
        :return: If return_content==True, the raw content will be returned as a byte string, else the command is return on success. 
        """
        # make sure the command is up-to-date
        self.refresh()

        if self.operation == 'DOWNLOAD' or self.operation == 'QUIT':
            self.logger.info("No results to get for '{}' operations".format(self.operation))
            return None
        elif self.filesize == 0:
            self.logger.info("Command complete. No output to collect.")
            return None

        # Proceed only if the server reports it has results
        r = requests.get(self._ls.server+'/command/download', cert=self._ls.cert, params={'result': self.server_file_path}).json()
        if 'error' in r:
            self.logger.warning("{}".format(r['error']))
            return False

        if chunk_size:
            self._ls.chunk_size = chunk_size

        if not file_path:
            file_path = self.server_file_path
        file_path = file_path[file_path.rfind('/')+1:] if file_path.startswith('data/') else file_path

        # Do we already have some of the result file?
        if os.path.exists(file_path):
            statinfo = os.stat(file_path)
            position = statinfo.st_size
            self.logger.info("Already have {} out of {} bytes. Resuming download from server.."
                             .format(position, self.filesize))
        else:
            self.logger.debug("getting results for {}".format(self.id))

        arguments = {'position': position, 'cid': self.id}
        headers = {"Accept-Encoding": '0'}

        if self.status != 'COMPLETE' and self.status != 'STARTED':
            self.logger.warning("Any results for commands in state={} can not be reliably streamed.".format(self.status))
            return requests.get(self._ls.server+'/command/download', cert=self._ls.cert, params=arguments).json()

        raw_bytes = None
        total_chunks, remaining_bytes = divmod(self.filesize - position, self._ls.chunk_size)
        with closing(requests.get(self._ls.server+'/command/download', cert=self._ls.cert, params=arguments, headers=headers, stream=True)) as r:
            try:
                r.raw.decode_content = True
                # are we returning the raw bytes?
                if return_content:
                    raw_bytes = b''
                    for i in range(total_chunks):
                        raw_bytes += r.raw.read(self._ls.chunk_size)
                    raw_bytes += r.raw.read(remaining_bytes)
                    return raw_bytes
                else:
                    with open(file_path, 'ba') as f:
                        for i in range(total_chunks):
                            data = r.raw.read(self._ls.chunk_size)
                            if self.operation == 'RUN' and print_run:
                                print(data.decode('utf-8'))
                            f.write(data)
                        final_chunk = r.raw.read(remaining_bytes)
                        if self.operation == 'RUN' and print_run:
                            print(final_chunk.decode('utf-8'))
                        f.write(final_chunk)
                        f.close()
            except Exception as e:
                self.logger.error(str(e))
                return False

        # Did we get the entire result file?
        filesize = os.stat(file_path).st_size
        if self.filesize == filesize:
            self.logger.info("Result file download complete. Wrote {}.".format(file_path))
            return True
        else:
            self.logger.info("Data stream closed prematurely. Have {}/{} bytes. Trying to resume..".
                              format(filesize, self.filesize))
            self.get_results()
        return None

    def wait_for_completion(self):
        """Wait for this command to complete by continously querying for its status to change to 'COMPLETE' with the server.

        :return: True when a command's status changes to 'COMPLETE'. 
        """
        while True:
            self.refresh()
            tmp_client = self._ls.get_client(self.client_id)
            #if tmp_client.status != 'ONLINE' and tmp_client.status != 'BUSY':
            if not tmp_client.is_online and not tmp_client.is_busy:
                self.logger.warning("This command's LERC ({} (ID:{})) has gone to a status of '{}'".format(self.hostname, self.client_id, tmp_client.status))
            if self.status == 'PENDING': # we wait
                self.logger.info("Command {} PENDING. Checking again in 10 seconds..".format(self.id))
                time.sleep(10)
            elif self.status == 'PREPARING': # the command needs something from us (file)
                if self.operation != "DOWNLOAD":
                    self.logger.error("Command {} is PREPARING but we don't know what for.".format(self.id))
                    return False
                self.logger.info("Command {} PREPARING. Streaming file to server..".format(self.id))
                # function to stream file to server
                if not self.analyst_file_path:
                    self.logger.error("Can't resume upload to server, analyst_file_path is not defined")
                    return False
                self.stream_file(self.analyst_file_path, self.file_position)
            elif self.status == 'STARTED':
                self.logger.info("Command {} STARTED. Checking again in 10 seconds..".format(self.id))
                time.sleep(10)
            elif self.status == 'COMPLETE':
                self.logger.info("Command {} COMPLETE.".format(self.id))
                return True
            else: # Only here if command in UNKNOWN or ERROR state
                self.logger.info("Command {} state: {}.".format(self.id, self.status))
                if self.status == 'ERROR':
                    err = self.get_error_report()
                    self.logger.warning("Error message for command={} : {}".format(self.id, err['error']))
                return None



class lerc_session():
    """Represents a Live Endpoint Response Client Server control session.
    This class is for interacting and managing the LERC clients and server.

    Optional arguments:

    :profile: Specifiy a group or company to work with. These are defined in the lerc.ini config file.
    :server: The name the LERC control server to work with. Default is read from the lerc.ini config file.
    :chunk_size: The chunk size to use when streaming files between a lerc_session and the LERC server

    """
    server = None
    logger = logging.getLogger(__name__+".lerc_session")

    def __init__(self, profile='default', server=None, chunk_size=4096):
        self.config = check_config(CONFIG, required_keys=['server', 'server_ca_cert', 'client_cert', 'client_key'])
        self.profile = profile
        if server:
            self.server = server
        else:
            self.server = self.config[profile]['server']
        if not self.server.startswith('https://'):
            self.server = 'https://' + self.server
        if self.server[-1] == '/':
            self.server = self.server[:-1]
        if 'server_ca_cert' in self.config[profile]:
            self.logger.debug("setting 'REQUESTS_CA_BUNDLE' environment variable for HTTPS verification")
            os.environ['REQUESTS_CA_BUNDLE'] = self.config[profile]['server_ca_cert']
        self.client_cert = self.config[profile]['client_cert']
        self.client_key = self.config[profile]['client_key']
        self.cert = (self.client_cert, self.client_key)
        if 'ignore_system_proxy' in self.config[profile]:
            if self.config[profile].getboolean('ignore_system_proxy'):
                # route direct
                if 'https_proxy' in os.environ:
                    del os.environ['https_proxy']
        self.chunk_size = chunk_size

    @property
    def get_config(self):
        return self.config

    @property
    def get_profile(self):
        return self.profile

    def query(self, **kwargs):
        """Query the lerc server database. Very simple queries supported.
        
        Note: The 'rc' field stands for return commands. By default, command results are only returned if 'rc' is set OR if a 'cmd*' field is set.

        Possible kwargs:

        :param str cmd_id: Command id
        :param str hostname: lerc hostname
        :param str operation: Lerc operation
        :param str cmd_status: Status of a command
        :param str client_id: ID of a lerc
        :param str client_status: Status of a lerc
        :param str version: lerc version
        :param str company_id: ID of a company/group that lercs are in
        :param str company: Name of a company/group that lercs are in
        """
        valid_fields = ['rc', 'cmd_id', 'hostname', 'operation', 'cmd_status', 'client_id', 'client_status', 'version', 'company_id', 'company']
        #valid_fields = QUERY_FIELDS.append('rc')
        keys = kwargs.keys()
        valid_keys = [key for key in keys if key in valid_fields]
        if len(valid_keys) <= 0:
            self.logger.warning("None of {} are valid query fileds.".format(keys))
            return False

        # If cmd keys were passed, assume it's ok to set the return commands arg
        if 'rc' not in keys:
            cmd_keys = [ key for key in valid_keys if 'cmd' in key]
            if len(cmd_keys) > 0:
                kwargs['rc'] = True

        self.logger.debug("Searching for client(s) meeting : {}".format(kwargs))
        r = requests.get(self.server+'/query', cert=self.cert, params=kwargs).json()
        results = {}
        if 'clients' in r:
            results['clients'] = [Client(c, profile=self.profile) for c in r['clients']]
            if 'commands' in r:
                results['commands'] = [Command(c, profile=self.profile) for c in r['commands']]
            if 'client_id_list' in r:
                results['client_id_list'] = r['client_id_list']
            return results
        return r

    def get_command(self, cid):
        """ Get a command by it's id.

        :param int cid: The id of a lerc command.
        :return: A lerc_api.Command object or False
        """
        r = self.query(cmd_id=cid, rc=True)
        # querying by command id should always return a single command
        if 'commands' in r and len(r['commands']) == 1:
            return r['commands'][0]
        self.logger.warning("No command result for {} : {}".format(cid, r))
        return False

    def get_host(self, hostname):
        """Query for a lerc by hostname. Return a Client object if one lerc is found, else a list of Clients.

        :param str hostname: The hostname of a lerc
        :return: False if no lerc by the hostname, a lerc_api.Client object if a sigle lerc, else a list of lerc_api.Clients
        """
        result = self.query(hostname=hostname)
        if 'clients' in result:
            if len(result['clients']) > 1:
                self.logger.error("More than one result for query by hostname")
                return result['client']
            elif len(result['clients']) == 1:
                return result['clients'][0]
            else:
                self.logger.info("No lerc found by this hostname: {}".format(hostname))
                return False

    def get_client(self, cid):
        """Get a client by it's id.

        :param int cid: The id of a lerc
        :return: A lerc_api.Client object of False
        """
        # should only ever return one lerc
        r = self.query(client_id=cid)
        if 'clients' in r and len(r['clients']) == 1:
            return r['clients'][0]
        self.logger.info("No Client with ID {} exists.".format(cid))
        return False

    def yield_hosts(self):
        """Yeild every lerc client the server knows about.
        """
        # The server will give us a list of valid client ids when we give a valid
        # query that returns no results -- a client by id zero does not exist.
        result = self.query(client_id=0)
        if 'client_id_list' not in result:
            self.logger.error("Unexpected result from lerc server : {}".format(result))
            return False
        client_ids = result['client_id_list']
        for id in client_ids:
            yield self.get_client(id)

