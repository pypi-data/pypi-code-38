
import os
import logging
import pprint
from lerc_control import lerc_api
from configparser import ConfigParser

logger = logging.getLogger("lerc_control."+__name__)

REQUIRED_CMD_KEYS = ['operation']
OPTIONAL_CMD_KEYS = ['wait_for_completion', 'get_results']

REQUIRED_OP_KEY_MAP = {'RUN': ['command'],
                       'UPLOAD': ['path'],
                       'DOWNLOAD': ['file_path'],
                       'QUIT': []}
OPTIONAL_OP_KEY_MAP = {'RUN': ['async_run', 'write_results_path'],
                       'UPLOAD': ['write_results_path'],
                       'DOWNLOAD': ['client_file_path'],
                       'QUIT': []}

# Get the working lerc_control directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def script_missing_required_keys(config, KEYS):
    for key in KEYS:
        for section in config.sections():
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

def execute_script(lerc, script_path):
    """Execute a script on this host.

    :param lerc_api.Client lerc: A lerc_api.Client object.
    :param str script_path: the path to the script
    :return: a dictionary of the commands issued
    """

    if not isinstance(lerc, lerc_api.Client):
        logger.error("Argument is of type:{} instead of type lerc_api.Client".format(type(lerc)))
        return False

    config = lerc._ls.get_config
    profile = lerc._ls.profile
    #default_client_dir = config[profile]['client_working_dir']

    script = ConfigParser()
    if not os.path.exists(script_path):
        if script_path[0] == '/':
            script_path = BASE_DIR + script_path
        else:
            script_path = BASE_DIR + '/' + script_path
    script.read(script_path)
 
    if script_missing_required_keys(script, REQUIRED_CMD_KEYS):
        return False

    command_history = {}

    script_name = script_path[script_path.rfind('/')+1:script_path.rfind('.')]
    # make sure requirements are met first
    for command in script.sections():
        op =  script[command]['operation'].upper()
        if op not in REQUIRED_OP_KEY_MAP:
            logger.error("{} is not a recognized lerc operation!".format(op))
            return False
        if operation_missing_required_keys(script, command, REQUIRED_OP_KEY_MAP[op]):
            return False

    logger.info("Beginning execution of {}".format(script_name))
    for command in script.sections():
        logger.info("Processing {}".format(command))
        command_history[command] = {}
        op =  script[command]['operation'].upper()

        get_results = False
        if 'get_results' in script[command]:
            get_results = script[command].getboolean('get_results')
        # should only ever be in run and upload commands
        write_results_path = None
        if 'write_results_path' in script[command]:
            write_results_path = script[command]['write_results_path']

        if op == 'RUN':
            async_run = False
            if 'async_run' in script[command]:
                async_run = script[command].getboolean('async_run')
            run_string = script[command]['command']
            cmd = lerc.Run(run_string, async=async_run)
            command_history[command] = cmd
            command_history[command].get_the_results = get_results
            command_history[command].write_results_path = write_results_path
            logger.info("Issued : Run - CID={} - {}".format(cmd.id, run_string))
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
            cmd = lerc.Download(file_path, client_file_path=client_file_path)
            command_history[command] = cmd
            logger.info("Issued : Download - CID={} - {}".format(cmd.id, file_path))
        elif op == 'UPLOAD':
            path = script[command]['path']
            # if the script doesn't specify the full path, add default client working dir
            #if '\\' not in path:
                #path = default_client_dir + path
            cmd = lerc.Upload(path)
            command_history[command] = cmd
            command_history[command].get_the_results = get_results
            command_history[command].write_results_path = write_results_path
            logger.info("Issued : Upload - CID={} - {}".format(cmd.id, path))
        elif op == 'QUIT':
            cmd = lerc.Quit()
            command_history[command] = cmd
            logger.info("Issued : Quit - CID={}".format(cmd.id, path))

    logger.info("Checking to see if results need to be obtained ...")
    for command in command_history:
        cmd = command_history[command]
        if hasattr(cmd, 'get_the_results') and cmd.get_the_results:
            logger.info("Waiting for command {} to complete..".format(cmd.id))
            cmd.wait_for_completion()
            logger.info("Getting the results for command {}".format(cmd.id))
            cmd.get_results(file_path=cmd.write_results_path)

    return command_history
