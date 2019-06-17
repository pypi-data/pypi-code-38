"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""
import base
import datetime
import json
import os
import sys
import settings
import time
import urllib
from subprocess import Popen, PIPE
from multiprocessing import Queue
from controllers import ClientInfo, BaseController
from base import BaseClient
from scope import ScopeClient
from base import safe_write
from base import c_diagnostic_logger as clogger
from command_runners import CommandRunner


BASE_URL = settings.BASE_URL
COMPANYNAME = settings.COMPANYNAME
DIRPATH = settings.DIRPATH
TMPDIR = settings.TMPDIR
COMMAND_FILE = settings.COMMAND_FILE
INSTRUCT_URL = BASE_URL + '/instructions.json'
COMMAND_URL = BASE_URL + '/commands'


# Set globals
SECONDS_BTW_HEALTH_UPDATES = 5
logger = base.logger
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def scope_client(client_info=None):
    """Starts the manager for getting and running configs"""
    if 'instrument_type' not in client_info.identity_dict:
        logger.warning("Missing instrument_type for ScopeClient. "
                       "No new process will be startd for {}"
                       .format(client_info.identity_dict))
        return
    logger.info("scope_client: initializing ScopeClient with: {}"
                .format(client_info.identity_dict))
    if not client_info:
        client_info = ClientInfo(
            target=scope_client,  # recursive target needed for restarts
            name='scope_client',
            keep_alive_interval=1200,
        )
    client = ScopeClient(client_info=client_info)
    client.run()


class HealthClient(BaseClient):

    def __init__(self, *args, **kwargs):
        self.name = 'health_client'
        self.prev_states = []
        super(HealthClient, self).__init__(name=self.name, *args, **kwargs)

    """Manages process that gateway health info updates"""
    def put_health_data(self):
        """makes PUT with the health data to server"""
        url = settings.BASE_URL + '/gateway'
        payload = {
            'id': settings.GATEWAY_ID,
            'company': COMPANYNAME,
            'status': 'Online',
            'instruments': self._check_instruments_needing_update(),
        }
        logger.info("Updating gateway health state with payload {}"
                    .format(payload))
        self.put(url, data=json.dumps(payload))

    def _check_instruments_needing_update(self):
        """Checks for instruments that need an update

        Summary:
            There is a special rule where an Offline instrument
            is only reported Offline once per change to Offline.
            If it was already previously Offline then no update
            to the server is required and thus this method will
            not return it as part of the list of instruments that
            need an update (to the server). All other statues
            will require an update to the server even if previously
            the same. For example, if it was Online and is still
            Online, an update is still needed to let the server
            know that the instrument has not timed out.

        Returns:
            A list of instruments needed for update to server
        """
        instruments = []  # list of instruments to update server
        states = self._read_instrument_states()
        for state in states:
            matches = [s for s in self.prev_states if s['id'] == state['id']]
            if not matches:
                # no matching prev state, append instruments with new state
                instruments.append(state)
            elif state['status'] != 'Offline':
                # only Offline has special rules, all others still need update
                instruments.append(state)
            elif matches[0]['status'] != 'Offline':
                # prev status was not 'Offline' so append to update the server
                instruments.append(state)
        self.prev_states = states
        # reset states file
        self._write_states_to_file([])
        return instruments

    def run(self, client_info):
        """Runs the health manager indefinitely"""
        clogger.info("Initial gateway health checking in as online: {}"
                     .format(settings.GATEWAY_ID))
        while True:
            logger.info("HealthClient is alive")
            self.put_health_data()
            self.post_logfile()
            self.update_activity_file()
            time.sleep(SECONDS_BTW_HEALTH_UPDATES)

    def get_client_version(self, package='gradientone'):
        """Gets version by parsing pip output"""
        if sys.platform == 'win32':
            import version
            return version.__version__
        v_dict = {}
        version_string = ''
        try:
            version_file = os.path.join(DIRPATH, 'version.py')
            with open(version_file, 'r') as f:
                exec(f.read(), v_dict)
            version_string = v_dict['__version__']
        except Exception as e:
            logger.warning("Unable to read version file %s" % e)
        if not version_string:
            pip_show_pkg = ['pip', 'show', package]
            try:
                output = Popen(pip_show_pkg, stdout=PIPE).communicate()[0]
            except Exception as e:
                logger.warning("Unable to read pip version %s" % e)
                return ""
            if output is None:
                logger.warning("No output from Popen in get_client_version")
                return ""
            lines = output.split('\n')
            for line in lines:
                if line.startswith("Version:"):
                    version_string = line.split(':')[1].strip()
        return version_string


def health_updates(client_info):
    """Runs the manager that posts gateway health info"""
    pid_file = os.path.join(TMPDIR, 'health_updates.pid')
    safe_write(pid_file, str(os.getpid()))
    client = HealthClient(client_info=client_info)
    client.run(client_info)


def special_commands(client_info):
    pid_file = os.path.join(TMPDIR, 'special_commands.pid')
    safe_write(pid_file, str(os.getpid()))
    client = SpecialCommandsClient(client_info=client_info)
    client.run(client_info)


class SpecialCommandsClient(BaseClient):

    def __init__(self, *args, **kwargs):
        super(SpecialCommandsClient, self).__init__(*args, **kwargs)
        self.name = 'SpecialCommandsClient'

    def run(self, client_info):
        while True:
            time.sleep(1)
            try:
                # check the command queue for new commands
                command = self.client_info.command_queue.get()
            except:
                continue
            try:
                self.run_special_command(command)
                self.update_activity_file()
            except Exception as e:
                logger.error("Unexpected exception %s" % e, exc_info=True)

    def run_special_command(self, command):
        if command['name'] == 'UpdateConfigFile':
            self.update_cfg(command)
        else:
            logger.warning("Unexpected command {}".format(command))

    def update_cfg(self, command):
        """Grabs the new config file from the server"""
        cfgfile = urllib.URLopener()
        cfgfile.retrieve(command.arg, settings.cfgfile)


class GatewayClient(BaseController, CommandRunner):

    def __init__(self, *args, **kwargs):
        """Initializes the gateway client

        Sets the keep alive interval and activity file for the
        Gateway Client. These will be used to keep the process
        running and 'alive'
        """
        name = 'gateway_client'
        super(GatewayClient, self).__init__(name=name, *args, **kwargs)
        # the number of seconds between each check in for seeing if
        # sub clients are still running
        self.keep_alive_check_inteval = 5
        self.activity_file = os.path.join(TMPDIR, name + '_activity.txt')
        self.asset_id = settings.GATEWAY_ID
        self.name = name
        self.command = None
        self.instrument = None
        self.instruction_id = None
        self.instrument_list = []  # list of instrument dicts
        self.instrument_ids = []  # list of instrument id strings
        self.path_to_commands = COMMAND_FILE
        url = INSTRUCT_URL + '?next=t&gateway=' + settings.GATEWAY_ID
        # to avoid picking up instrument specific commands use 'default'
        url += '&instrument_id=default'
        self.instructions_url = url
        self.states = []

    def _reset_states_file(self):
        """Clears the instrument states file

        This is called when the client is started to remove any old
        data that might have been leftover from a previous client run
        that was interrupted.
        """
        logger.info("resetting states file: {}".format(settings.STATES_FILE))
        with open(settings.STATES_FILE, 'w') as f:
            f.write(json.dumps([]))

    def start_client_processes(self):
        """Starts the clients and keeps them alive

        Gathers the client infos to run with controller and starts up
        the sub clients with each client info object.

        The targets and names are used to create ClientInfo objects used in
        the BaseController run() method. The keep_alive_interval
        is the seconds allowed to pass between updates to the activity file
        before the controller will restart the client process.

        Note that the BaseController will pass the ClientInfo object
        to the target function so that the function will have the client
        info, most importantly the activity_file that it needs to update
        periodically within the keep_alive_interval

        Lastly, calls run_main_instructions_loop() to run the main
        loop that checks for instructions and keeps the client
        processes alive
        """
        self._reset_states_file()
        self.client_infos = []
        hposts_info = ClientInfo(
            target=health_updates,
            name='health_updates',
            keep_alive_interval=120,
        )
        logger.info("start_client_processes() Starting HealthClient")
        self._start_sub_client(hposts_info)
        inst_list = self._detect_instruments()
        for inst_dict in inst_list:
            pid = self._start_instr_client(inst_dict)
            inst_dict['pid'] = pid
            self.instrument_list.append(inst_dict)
            self.instrument_ids.append(inst_dict['id'])

        # start the main loop for gateway (not instrument) instructions
        self.run_main_instructions_loop()

    def _start_instr_client(self, inst_dict):
        """Starts an instrument client process from dictionary"""
        inst_client_info = ClientInfo(
            target=scope_client,
            name=inst_dict['id'] + '_client',
            keep_alive_interval=2400,
            identity_dict=inst_dict,
        )
        logger.info("Starting {}".format(inst_client_info.name))
        return self._start_sub_client(inst_client_info)

    def _start_sub_client(self, client_info):
        """Starts a sub client process for given client info

        Summary:
            This can be used for any sub client process, including
            the general health client process and instrument clients

        Parameters:
            client_info - object containing information about the
                sub client process to start
        """
        pid = self.start_process(
            target=client_info.target,
            name=client_info.name,
            ps_args=(client_info,),
        )
        return pid

    def run_main_instructions_loop(self):
        """starts the loop that checks for instructions"""
        logger.info("beginning main loop for requesting instructions "
                    "from the server")
        clogger.info("Starting Main Instruction Loop")
        second_counter = 0
        self._remove_command_file()  # remove any stale command files
        while True:
            self._check_for_state_change()
            self._handle_instructions()
            # check for any pending commands to start running
            if os.path.exists(self.path_to_commands):
                self._handle_command_file(self.path_to_commands)
            time.sleep(1)
            second_counter += 1
            self.update_activity_file()

    def _check_for_state_change(self):
        """Checks the states file for state changes to handle

        Summary:
            Reads the states file to check for state changes of
            instruments. If an instrument goes from Offline to
            Online it's important that an instrument client
            process is started for that instrument. Also if a
            new instrument is detected then an instrument
            client process needs to be started. Finally, after
            comparing the latest states with previous ones, this
            method updates the instrument_list class attribute
            with the latest states.
        """
        latest_states = self._read_instrument_states()
        for state in latest_states:
            if state['id'] in self.instrument_ids:
                idx = self.instrument_ids.index(state['id'])
                old_state = self.instrument_list[idx]
                self._compare_states(old_state, state)
                self.instrument_list[idx].update(state)
            else:
                # else it's a new instrument so start a client
                pid = self._start_instr_client(state)
                state['pid'] = pid
                self.instrument_list.append(state)
                self.instrument_ids.append(state['id'])

    def _compare_states(self, old_state, new_state):
        """Compares two instrument states and handles accordingly

        Summary:
            If the state's status changed from Offline to Ready
            then a new instrument client process is started for
            the instrument.
        """
        if 'status' not in old_state:
            old_state['status'] = 'Offline'
            logger.warning("status was not recorded in old state: {}; "
                           "assigning old status=Offline ".format(old_state))
        if old_state['status'] == 'Offline' and new_state['status'] == 'Ready':
            self._start_instr_client(new_state)

    def keep_clients_alive(self):
        """Checks in with each client to keep alive

        If a client process has not checked in with the
        activity file within it's keep alive interval, then
        the client process is restarted

        Then this function checks the activity files of each client
        for if they are still updating. If the time (seconds) since the
        last update to a given client's activity file was longer than
        that client's keep_alive_interval then the client process is
        restarted. As part of the restart, the client's activity file
        is updated with the current time.
        """
        for client_info in self.client_infos:
            c_time = datetime.datetime.now()
            fmt = DATETIME_FORMAT
            act_time_str = self.read(client_info.activity_file)
            if act_time_str:
                try:
                    act_time = datetime.datetime.strptime(act_time_str, fmt)
                except Exception as e:
                    logger.warning("Activity time exception: %s" % e)
                    act_time = c_time
            else:
                act_time = c_time
            elapsed_secs = (c_time - act_time).total_seconds()
            grace_period = client_info.keep_alive_interval
            if elapsed_secs > grace_period:
                name = client_info.name
                logger.warning(
                    "{} timed out after {} seconds. The keep alive interval "
                    "for this process is {}"
                    .format(name, elapsed_secs, grace_period)
                )
                self.restart_process(target=client_info.target, name=name,
                                     ps_args=(client_info,))
                logger.info("restarting process for %s" % name)
                self.write(client_info.activity_file, c_time.strftime(fmt))



###################################################################

# Start of sample code, not part of normal gateway client operation

###################################################################


def simple_client_a(client_info):
    while True:
        logger.info("Simple client A checking command q:")
        try:
            command = client_info.command_queue.get(block=False)
        except:
            command = None
        if command:
            logger.info("Simple client A command:")
            logger.info(command)
        time.sleep(1)


def simple_client_b(client_info):
    while True:
        logger.info("Simple client B checking command q:")
        try:
            command = client_info.command_queue.get(block=False)
        except:
            command = None
        if command:
            logger.info("Simple client B command:")
            logger.info(command)
        time.sleep(1)


class SimpleExample(BaseController):

    def __init__(self, *args, **kwargs):
        name = 'simple example'
        super(SimpleExample, self).__init__(name=name, *args, **kwargs)
        self.command_queue_a = Queue()
        info_a = ClientInfo(
            target=simple_client_a,
            name='simple_client_a',
            keep_alive_interval=1200,
            command_queue=self.command_queue_a,
        )
        self.command_queue_b = Queue()
        info_b = ClientInfo(
            target=simple_client_b,
            name='simple_client_b',
            keep_alive_interval=120,
            command_queue=self.command_queue_b,
        )
        self.client_infos = [info_a, info_b]

        # Other clients to be run by the BaseController should
        # be added here. Be sure to create a ClientInfo object with
        # the appropriate target, name, keep_alive_interval, and
        # activity file. Then append the object to client_infos

        # These client_info's will specify the client processes to be started
        # when the BaseController method start_client_processes() is called

    def sample_start_sub_client_processes(self):
        """SAMPLE of the main run method of SimpleExample"""
        self.command_queue_a.put({'number': 1})
        time.sleep(1)
        self.command_queue_b.put({'number': 1})
        time.sleep(1)
        self.command_queue_a.put({'number': 2})
        time.sleep(1)
        self.command_queue_a.put({'number': 3})
        time.sleep(1)
        self.command_queue_b.put({'number': 2})
        time.sleep(1)
        self.command_queue_b.put({'number': 3})


###################################################################

# End of sample code

###################################################################


if __name__ == "__main__":
    client = GatewayClient()
    client.start_client_processes()
