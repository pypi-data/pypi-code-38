
import os
import logging
import pprint
from lerc_control import lerc_api
from configparser import ConfigParser

logger = logging.getLogger("lerc_control."+__name__)

IGNORED_SECTIONS = ['overview']
REQUIRED_CMD_KEYS = ['operation']
OPTIONAL_CMD_KEYS = ['wait_for_completion', 'get_results']

REQUIRED_OP_KEY_MAP = {'RUN': ['command'],
                       'UPLOAD': ['path'],
                       'DOWNLOAD': ['file_path'],
                       'QUIT': []}
OPTIONAL_OP_KEY_MAP = {'RUN': ['async_run', 'write_results_path', 'print_results',
                               'common_setup_command', 'common_cleanup_command'],
                       'UPLOAD': ['write_results_path'],
                       'DOWNLOAD': ['client_file_path', 'common_setup_command'],
                       'QUIT': ['common_cleanup_command']}

# Get the working lerc_control directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def script_missing_required_keys(config, KEYS):
    for key in KEYS:
        for section in config.sections():
            if section in IGNORED_SECTIONS:
                return False
            if not config.has_option(section, key):
                logger.error("{} is missing required key: {}".format(section, key))
                return True
    return False

def operation_missing_required_keys(config, section, KEYS):    
    for key in KEYS:
        if not config.has_option(section, key):
            logger.error("{} is missing required operation key:{} for operation:{}".format(section, key, config[section]['operation']))
            return True
    return False


def get_script_results(cmds):
    """
    Wait for and collect results from the given list of script commands.
    """
    written_result_cmds = []
    for cmd in cmds:
        logger.info("Waiting for command {} to complete..".format(cmd.id))
        cmd.wait_for_completion()
        logger.info("Getting the results for command {}".format(cmd.id))
        cmd.get_results(file_path=cmd.write_results_path, print_run=cmd.print_results)
        if cmd.write_results_path and os.path.exists(cmd.write_results_path):
            logger.info("Wrote results: {}".format(cmd.write_results_path))
            written_result_cmds.append(cmd)
    return written_result_cmds


def load_script(script_path):
    script = ConfigParser()
    if not os.path.exists(script_path):
        if script_path[0] == '/':
            script_path = BASE_DIR + script_path
        else:
            script_path = BASE_DIR + '/' + script_path
    if not os.path.exists(script_path):
        script_name = script_path[script_path.rfind('/')+1:script_path.rfind('.')]
        logger.error("The path to the script named '{}' does not exist.".format(script_name))
        return False
    try:
        script.read(script_path)
    except Exception as e:
        logger.error("ConfigParser Error reading '{}' : {}".format(script_path, e))
        return False
    return script

# Global variables
COMMON_SETUP_COMMANDS = {'RUN': [],
                         'DOWNLOAD': []}
COMMON_CLEANUP_COMMANDS = {'RUN': [],
                           'QUIT': []}

def execute_script(lerc, script_path, return_result_commands=False, execute_cleanup_commands=True):
    """Execute a script on this host.

    :param lerc_api.Client lerc: A lerc_api.Client object.
    :param str script_path: the path to the script
    :param bool return_result_commands: If True, return list of commands that we need to get results from.
    :param bool execute_cleanup_commands: common_cleanup_commands will be executed if True. Else they're stored in COMMON_CLEANUP_COMMANDS
    :return: a dictionary of the commands issued
    """

    if not isinstance(lerc, lerc_api.Client):
        logger.error("Argument is of type:{} instead of type lerc_api.Client".format(type(lerc)))
        return False

    config = lerc._ls.get_config
    profile = lerc._ls.profile
    #default_client_dir = config[profile]['client_working_dir']
 
    script = load_script(script_path)

    if script_missing_required_keys(script, REQUIRED_CMD_KEYS):
        return False

    command_history = {}
    commands = [cmd for cmd in script.sections() if cmd not in IGNORED_SECTIONS]

    script_name = script_path[script_path.rfind('/')+1:script_path.rfind('.')]
    # make sure requirements are met first
    for command in commands:
        op =  script[command]['operation'].upper()
        if op not in REQUIRED_OP_KEY_MAP:
            logger.error("{} is not a recognized lerc operation!".format(op))
            return False
        if operation_missing_required_keys(script, command, REQUIRED_OP_KEY_MAP[op]):
            return False

    logger.info("Beginning execution of {}".format(script_name))
    for command in commands:
        logger.info("Processing {}".format(command))
        command_history[command] = {}
        op =  script[command]['operation'].upper()

        print_results = True
        get_results = False
        write_results_path = None
        is_common_setup_command = False
        is_common_cleanup_command = False
        message = False
        if 'get_results' in script[command]:
            get_results = script[command].getboolean('get_results')
        if 'write_results_path' in script[command]:
            write_results_path = script[command]['write_results_path'].format(HOSTNAME=lerc.hostname)
        if 'common_setup_command' in script[command]:
            is_common_setup_command = script[command].getboolean('common_setup_command')
        if 'common_cleanup_command' in script[command]:
            is_common_cleanup_command = script[command].getboolean('common_cleanup_command')
        if 'message' in script[command]:
            message = script[command]['message'].format(HOSTNAME=lerc.hostname)

        if op == 'RUN':
            async_run = False
            if 'async_run' in script[command]:
                async_run = script[command].getboolean('async_run')
            if 'print_results' in script[command]:
                print_results = script[command].getboolean('print_results')
            run_string = script[command]['command']
            if is_common_setup_command:
                cmd = [cmd for cmd in COMMON_SETUP_COMMANDS['RUN'] if run_string == cmd.command]
                if cmd:
                    if len(cmd) != 1:
                        logger.error("Logic error - more than one common command with the same setup command: {}".format(cmd))
                    cmd = cmd[0]
                    logger.info('Skipping common setup command for script:{} as it should already be satisfied by: CMD={} -> {}'.format(script_name, cmd.id, cmd.command))
                    continue
            if is_common_cleanup_command and not execute_cleanup_commands:
                cmd = [cmd_string for cmd_string in COMMON_CLEANUP_COMMANDS['RUN'] if run_string == cmd_string]
                if not cmd:
                    # assuming we never will want to async_run OR write_results_path OR print_results
                    COMMON_CLEANUP_COMMANDS['RUN'].append(run_string)
                continue
            cmd = lerc.Run(run_string, async=async_run)
            command_history[command] = cmd
            command_history[command].get_the_results = get_results
            command_history[command].write_results_path = write_results_path
            command_history[command].print_results = print_results
            command_history[command].is_common_setup_command = is_common_setup_command
            if is_common_setup_command:
                COMMON_SETUP_COMMANDS['RUN'].append(cmd)
            logger.info("Issued : Run - CID={} - {}".format(cmd.id, run_string))
            if message:
                logger.info("SCRIPT MESSAGE: {}".format(message))
        elif op == 'DOWNLOAD':
            client_file_path = None
            if 'client_file_path' in script[command]:
                client_file_path = script[command]['client_file_path']
            file_path = script[command]['file_path']
            if not os.path.exists(file_path):
                old_fp = file_path
                if file_path[0] == '/':
                    file_path = BASE_DIR + file_path
                else:
                    file_path = BASE_DIR + '/' + file_path
                if not os.path.exists(file_path):
                    logger.error("Not found: '{}' OR '{}'".format(old_fp, file_path))
                    return False
            if is_common_setup_command:
                cmd = [cmd for cmd in COMMON_SETUP_COMMANDS['DOWNLOAD'] if file_path == cmd.analyst_file_path]
                if client_file_path and cmd:
                    cmd2 = [cmd for cmd in COMMON_SETUP_COMMANDS['DOWNLOAD'] if client_file_path == cmd.client_file_path]
                    if cmd2 and cmd[0].id != cmd2[0].id:
                        logger.debug("Similar but different setup commands issued previously.")
                        # we should issue a new command
                        cmd = None
                if cmd:
                    if len(cmd) != 1:
                        logger.warning("Logic error - more than one common command with the same setup command: {}".format(cmd))
                    cmd = cmd[0]
                    logger.info('Skipping common setup command for script:{} as it should already be satisfied by: CMD={} to download {}'.format(script_name, cmd.id, cmd.analyst_file_path))
                    continue
            cmd = lerc.Download(file_path, client_file_path=client_file_path)
            command_history[command] = cmd
            command_history[command].is_common_setup_command = is_common_setup_command
            if is_common_setup_command:
                COMMON_SETUP_COMMANDS['DOWNLOAD'].append(cmd)
            logger.info("Issued : Download - CID={} - {}".format(cmd.id, file_path))
            if message:
                logger.info("SCRIPT MESSAGE: {}".format(message))
        elif op == 'UPLOAD':
            path = script[command]['path']
            # if the script doesn't specify the full path, add default client working dir
            #if '\\' not in path:
                #path = default_client_dir + path
            cmd = lerc.Upload(path)
            command_history[command] = cmd
            command_history[command].get_the_results = get_results
            command_history[command].write_results_path = write_results_path
            command_history[command].print_results = False
            logger.info("Issued : Upload - CID={} - {}".format(cmd.id, path))
            if message:
                logger.info("SCRIPT MESSAGE: {}".format(message))
        elif op == 'QUIT':
            if is_common_cleanup_command and not execute_cleanup_commands:
                if not COMMON_CLEANUP_COMMANDS['QUIT']:
                    COMMON_CLEANUP_COMMANDS['QUIT'].append(run_string)
                continue
            cmd = lerc.Quit()
            command_history[command] = cmd
            logger.info("Issued : Quit - CID={}".format(cmd.id))
            if message:
                logger.info("SCRIPT MESSAGE: {}".format(message))

    logger.info("Checking to see if results need to be obtained ...")
    result_commands = []
    for command in command_history:
        cmd = command_history[command]
        if hasattr(cmd, 'get_the_results') and cmd.get_the_results:
            if return_result_commands:
                result_commands.append(cmd)
            else:
                logger.info("Waiting for command {} to complete..".format(cmd.id))
                cmd.wait_for_completion()
                logger.info("Getting the results for command {}".format(cmd.id))
                cmd.get_results(file_path=cmd.write_results_path, print_run=cmd.print_results)
                if cmd.write_results_path and os.path.exists(cmd.write_results_path):
                    logger.info("Wrote results: {}".format(cmd.write_results_path))

    if return_result_commands:
        return result_commands
    return command_history
