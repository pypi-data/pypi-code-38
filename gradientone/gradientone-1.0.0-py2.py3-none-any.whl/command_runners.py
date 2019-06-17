"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""

import base
import collections
import datetime
import json
import os
import socket
import time
import traceback
import usb

import ivi_instruments
import settings

from base import BaseClient
from base import c_diagnostic_logger as clogger
from base import t_diagnostic_logger as tlogger
from base import ReadSettingsError, WriteSettingsError, FetchWaveformError
from base import FetchMeasurementError
from device_drivers.scope_driver import ScopeDriver
from device_drivers.keysight.keysightMSO9064A import KeysightMSO9064A
from device_drivers.keysight.keysightMSO9104A import KeysightMSO9104A
from device_drivers.rigol.rigolDS1000Z import RigolDS1000Z
from device_drivers.rigol.rigolDS1000ZPlus import RigolDS1000ZPlus
from device_drivers.rigol.rigolMSO1000Z import RigolMSO1000Z
from device_drivers.rigol.rigolDS2000A import RigolDS2000A
from device_drivers.rigol.rigolMSO2000A import RigolMSO2000A
from device_drivers.rigol.rigolMSO5002 import RigolMSO5002
from device_drivers.rigol.rigolMSO5004 import RigolMSO5004
from device_drivers.rigol.rigolDS7000 import RigolDS7000
from device_drivers.rigol.rigolMSO7000 import RigolMSO7000
from device_drivers.rigol.rigolMSO8000 import RigolMSO8000
from device_drivers.tektronix.tektronixDPO2002B import TektronixDPO2002B
from device_drivers.tektronix.tektronixDPO2004B import TektronixDPO2004B
from device_drivers.tektronix.tektronixDPO3014 import TektronixDPO3014
from device_drivers.tektronix.tektronixDPO3034 import TektronixDPO3034
from device_drivers.tektronix.tektronixMDO3012 import TektronixMDO3012
from device_drivers.tektronix.tektronixMDO3014 import TektronixMDO3014
from device_drivers.tektronix.tektronixMDO4104 import TektronixMDO4104
from device_drivers.tektronix.tektronixMSO2002B import TektronixMSO2002B
from device_drivers.tektronix.tektronixMSO2004B import TektronixMSO2004B
from device_drivers.tektronix.tektronixMSO5204B import TektronixMSO5204B
from transmitters import ScopeTransmitter

DRIVERS = {
    'TektronixDPO2002B': TektronixDPO2002B,
    'TektronixDPO2012': TektronixDPO2002B,
    'TektronixDPO2012B': TektronixDPO2002B,
    'TektronixDPO2022B': TektronixDPO2002B,
    'TektronixDPO2004B': TektronixDPO2004B,
    'TektronixDPO2014': TektronixDPO2004B,
    'TektronixDPO2024': TektronixDPO2004B,
    'TektronixDPO2024B': TektronixDPO2004B,
    'TektronixMSO2002B': TektronixMSO2002B,
    'TektronixMSO2012': TektronixMSO2002B,
    'TektronixMSO2012B': TektronixMSO2002B,
    'TektronixMSO2022B': TektronixMSO2002B,
    'TektronixMSO2004B': TektronixMSO2004B,
    'TektronixMSO2014': TektronixMSO2004B,
    'TektronixMSO2014B': TektronixMSO2004B,
    'TektronixMSO2024': TektronixMSO2004B,
    'TektronixMSO2024B': TektronixMSO2004B,
    'TektronixMDO3012': TektronixMDO3012,
    'TektronixMDO3022': TektronixMDO3012,
    'TektronixMDO3032': TektronixMDO3012,
    'TektronixMDO3052': TektronixMDO3012,
    'TektronixMDO3102': TektronixMDO3012,
    'TektronixMDO3014': TektronixMDO3014,
    'TektronixMDO3024': TektronixMDO3014,
    'TektronixMDO3034': TektronixMDO3014,
    'TektronixMDO3054': TektronixMDO3014,
    'TektronixMDO3104': TektronixMDO3014,
    'TektronixMSO5204B': TektronixMSO5204B,
    'TektronixDPO3014': TektronixDPO3014,
    'TektronixDPO3034': TektronixDPO3034,
    'KeysightMSO9064A': KeysightMSO9064A,
    'KeysightMSO9104A': KeysightMSO9104A,
    'TektronixMDO4104': TektronixMDO4104,
    'RigolDS1054Z': RigolDS1000Z,
    'RigolDS1074Z': RigolDS1000Z,
    'RigolDS1104Z': RigolDS1000Z,
    'RigolDS1074Z Plus': RigolDS1000ZPlus,
    'RigolDS1104Z Plus': RigolDS1000ZPlus,
    'RigolMSO1074Z': RigolMSO1000Z,
    'RigolMSO1104Z': RigolMSO1000Z,
    'RigolDS2072A': RigolDS2000A,
    'RigolDS2102A': RigolDS2000A,
    'RigolDS2202A': RigolDS2000A,
    'RigolDS2302A': RigolDS2000A,
    'RigolMSO2072A': RigolMSO2000A,
    'RigolMSO2102A': RigolMSO2000A,
    'RigolMSO2202A': RigolMSO2000A,
    'RigolMSO2302A': RigolMSO2000A,
    'RigolMSO5072': RigolMSO5002,
    'RigolMSO5074': RigolMSO5004,
    'RigolMSO5102': RigolMSO5002,
    'RigolMSO5104': RigolMSO5004,
    'RigolMSO5204': RigolMSO5004,
    'RigolMSO5354': RigolMSO5004,
    'RigolDS7014': RigolDS7000,
    'RigolDS7024': RigolDS7000,
    'RigolDS7034': RigolDS7000,
    'RigolDS7054': RigolDS7000,
    'RigolMSO7014': RigolMSO7000,
    'RigolMSO7024': RigolMSO7000,
    'RigolMSO7034': RigolMSO7000,
    'RigolMSO7054': RigolMSO7000,
    'RigolMSO8064': RigolMSO8000,
    'RigolMSO8104': RigolMSO8000,
    'RigolMSO8204': RigolMSO8000,
    'GenericScope': ScopeDriver
}


BASE_URL = settings.BASE_URL
COMMAND_FILE = settings.COMMAND_FILE
DEFAULT_TEK_TYPE = settings.DEFAULT_TEK_TYPE


# Careful! Setting BREATH_TIME any lower can cause issues.
# The 'instance hours' issue can happen by repeatedly
# making 100 requests per second and every second.
# HTTPS requests don't work that quickly anyway,
# so going lower than 0.25 is a waste of bandwidth
BREATH_TIME = 0.25
MAX_RETRIES = 5

CANBUS_URL = BASE_URL + "/motor/canbus"
INSTRUCT_URL = BASE_URL + '/instructions.json'
COMMAND_URL = BASE_URL + '/commands'

logger = base.logger


class CommandRunner(BaseClient):

    """CommandRunner runs the 'test' instructions form the server

       Note that a 'test' is not always an actual pass/fail test,
       the 'test' could be a configured scope waveform trace, or
       just a powermeter reading, or instructions for a motor, etc.

       run_command - this is the top level function that gets
                       when the client code creates a command
       single_run - most test runs will call this for a single run
       get_trace - when a trace is needed from the instrument,
                   this uses a device driver for the instrument
                   to pass instructions and get the trace data,
                   then returns a Transmitter to send to server
    """

    def __init__(self, client_info=None, command=None, instrument=None,
                 instrument_id='', *args, **kwargs):
        super(CommandRunner, self).__init__(*args, **kwargs)
        self.command = command
        self.timer = base.Timer()  # sets and clears command timeouts
        self.logger = logger
        self.instrument = instrument
        self.asset_id = instrument_id

        # path to commands can be overridden by sub clients for each
        # individual instrument process that has its own commands
        self.path_to_commands = COMMAND_FILE

        self.skip_http_reqs = False

    def update_command_status(self, status):
        data = {
            'command_id': self.command['id'],
            'status': status,
        }
        logger.info("Updating {} to {} status"
                    .format(self.command['id'], data['status']))
        self.put(BASE_URL + '/commands', data=json.dumps(data))

    def run_command(self):
        """Runs the CommandRunners command

        Returns:
            None: always returns None
        """
        if self.command['name'] == 'run_diagnostic':
            self._handle_gateway_diagnostic_command()
            return None
        elif self.command['name'] == 'detect_instruments':
            self._handle_detect_instruments_cmd()
            return None
        elif self.command['name'] == 'scpi_commands':
            self._handle_scpi_script()
            return None
        self.update_command_status(status='in progress')
        trace_dict = None
        if self.command['name'] == 'fetch_screenshot':
            tlogger.info("Handling screenshot fetch command")
            self.handle_screenshot_command()
        else:
            tlogger.info("Handling a trace command")
            trace_dict = self.get_trace()
        if trace_dict:
            logger.info("trace fetched for command: {}"
                        .format(self.command['id']))
            # build transmitter to return and eventually transmit trace
            tlogger.info("Preparing to transmit results: building transmitter")
            transmitter = ScopeTransmitter(trace_dict)
            # certain commands need transmit configuration for server storage
            if self.command['name'] in ['Capture', 'Autoset', 'Quickset']:
                tlogger.info("Transmitting config information")
                transmitter.transmit_config()
            # the trace transmitter will eventually mark the command complete
            transmitter.transmit_trace()
        else:
            # if it's not a trace we can just marke the command complete here
            data = {'id': self.command['id'], 'status': 'complete'}
            self.put(COMMAND_URL, data=json.dumps(data))
        file_key = self.command['id'] + '-diagnostic.log'
        self.transmit_file(tlogger.filepath, file_key=file_key)
        return None

    def _handle_scpi_script(self):
        """Overridden in scope.py ScopeClient"""
        pass

    def gen_data(self):
        command_id = self.command["id"]
        if command_id == 0:
            raise ValueError("Test run id is zero! Setup is:" + str(
                self.command))
        return {"command_id": command_id}

    def _remove_command_file(self):
        if not os.path.exists(self.path_to_commands):
            logger.debug("No command file to remove")
            return
        try:
            # remove the file after reading
            os.remove(self.path_to_commands)
        except OSError as e:
            logger.debug("OSError removing command file: {}".format(e))

    def _create_driver(self):
        """Creates a driver object with command and isntrument"""
        driver = None
        instrument_type = self.command['info']['instrument_type']
        logger.info("Getting driver for {}".format(instrument_type))
        try:
            driver = DRIVERS[instrument_type](self.command, self.instrument)
        except KeyError:
            logger.error("instrument_type {} not supported"
                         .format(self.command['info']['instrument_type']))
        except socket.error as e:
            tlogger.info("Instrument driver socket error {}".format(e))
            logger.info("unable to build driver: socket error {}".format(e))
        except Exception:
            logger.info("unable to build driver... no trace")
            logger.info(traceback.format_exc())
        return driver

    def update_instrument_status(self, status, local_only=False):
        data = {
            'id': self.asset_id,
            'status': status
        }
        logger.info("updating instrument status: {}".format(data))
        oldstates = self._read_instrument_states()
        states = self._update_states(oldstates, data)
        self._write_states_to_file(states)
        url = BASE_URL + '/assets'
        logger.info("update_instrument_status with {}".format(data))
        if not local_only:
            self.put(url, data=json.dumps(data))

    def handle_screenshot_command(self):
        # get the driver to pass commands to the isntrument
        driver = self._create_driver()
        if not driver:
            tlogger.info("Instrument driver error")
            return
        # fetch the screenshot from the instrument and post to server
        driver.fetch_screenshot()

    def get_trace(self):
        """ Gets a trace from the instrument.

            This uses a Driver for the instrument to pass
            instructions and get the trace data, then returns a
            trace object. The trace object is an instance of
            Transmitter that transmits the trace results and test
            run related data. By default it will retry once in case
            it fails on the first try.
        """
        # get driver for instrument
        tlogger.info("Getting the instrument driver")
        driver = self._create_driver()
        if not driver:
            msg = "Unable to get driver. Closing instrument"
            tlogger.info(msg)
            self._log_activity(msg, level='error')
            self.update_commands(status='failed', message=msg)
            return
        # get trace from instrument by running setup with driver
        trace_dict = None
        tlogger.info("Running driver: %s" % driver)
        try:
            trace_dict = self.run_driver(driver)
        except KeyError:
            self._handle_trace_error("KeyError in running setup",
                                     exc_info=True)
        except socket.error as e:
            self._handle_trace_error("Socket Error: {};".format(e))
        except ReadSettingsError as e:
            self._handle_trace_error("ReadSettingsError: Capture Failed, "
                                     "Unable To Get Instrument Settings",
                                     exc_info=True)
        except WriteSettingsError as e:
            self._handle_trace_error("WriteSettingsError: Capture Failed, "
                                     "Unable To Configure Instrument Settings",
                                     exc_info=True)
        except FetchWaveformError as e:
            self._handle_trace_error(
                "FetchWaveformError: Capture Failed, "
                "No Waveform Captured. Confirm Setup and Try Again",
                exc_info=True,
            )
        except Exception:
            self._handle_trace_error("Unexpected Error in get_trace",
                                     exc_info=True)
        else:
            tlogger.info("Instrument driver ran without error.")
        finally:
            return trace_dict

    def _handle_trace_error(self, message, exc_info=False):
        self._log_activity(message, level='error', exc_info=exc_info)
        self.update_commands(status='failed', message=message)
        self.update_instrument_status(status="Offline")

    def get_initial_excerpt(self, driver):
        """Returns the intial config excerpt from instrument

        It's important to call this before fetching measurements.
          1) It initializes the instrument and syncs up driver
          2) It gets an initial state, which is good for debugging

        driver: object that reads back the appropriate
                       fields for the instrument type

        """
        self.timer.set_timeout(240)
        initial_excerpt = None
        try:
            initial_excerpt = driver.get_config_excerpt()
            msg = "initial config setup from instrument: %s" % initial_excerpt
            logger.debug(msg)
        except usb.core.USBError as e:
            logger.debug("USBError!")
            driver.handle_usb_error(e)
        except ReadSettingsError as e:
            raise e
        except Exception:
            self.timer.clear_timeout()
            logger.debug("exception in config_excerpt initialization")
            raise ReadSettingsError()
        else:
            self.timer.clear_timeout()
            return initial_excerpt

    def _prepare_capture(self, driver, trace_dict):
        logger.debug("Peparing Capture without loading config")
        driver.check_scope_acquisition_length()
        driver.check_any_channel_enabled()

    def _prepare_autoset(self, driver, trace_dict):
        logger.debug("Loading Autoset")
        driver.load_autoset()
        logger.debug("Autoset loaded successfully")

    def _prepare_quickset(self, driver, trace_dict):
        logger.debug("Loading Quickset")
        driver.load_quickset()
        logger.debug("Quickset loaded successfully")

    def _get_server_instructions(self):
        """Checks instructions from server

        Summary:
            Uses the instructions_url class attribute.
            If an instrument_id is available, as is the case when
            there is an instrument with a Ready status, then the
            instrument_id is used to request instructions that are
            designated for the instrument. If no instrument_id is
            available, such as if there are no instruments detected
            upon initial boot up of the client, the gateway_id is
            used so that the server can send down "Discover" commands
            to detect instruments.
        """
        try:
            instructions = json.loads(self.get(self.instructions_url).text)
        except AttributeError:
            # can happen if no response from server
            clogger.info("AttributeError reading instructions json")
            return
        except TypeError:
            # can happen if instructions is None or no response
            clogger.info("TypeError reading instructions json")
            return
        except ValueError:
            # can happen if instructions is invalid JSON
            clogger.info("ValueError reading instructions json")
            return
        except Exception as e:
            clogger.info("Unexpected error reading instructions {}".format(e))
            return
        if not instructions:
            # uncomment to log every check for instructions (noisy)
            # logger.debug("No instructions at this time")
            return
        tlogger.refresh()
        if 'info' not in instructions:
            tlogger.warning("Empty instructions from server")
            return
        else:
            tlogger.info("Server instructions received")
            return instructions

    def _validate_instruction_info(self, instructions):
        if not instructions['info']:
            instructions['info'] = collections.defaultdict(str)
        if "id" not in instructions['info']:
            # the id was at the top level because it was a flat plan
            # i.e. a single command
            instructions['info']["id"] = self.instruction_id
        return instructions['info']

    def _detect_instruments(self):
        """Detects connected instruments and data about them

        Summary:
            Detects connected instruments. After detection,
            posts a client_diagnostic.log file to the server.
            When detecting an instruument it's status is ass

        Returns:
            A list of dictionaries, one for each connected instrument
            containing data about that instrument
        """
        logger.info("Detecting instruments...")
        scopes = ivi_instruments.get_connected_scopes()
        if settings.SIMULATED:
            inst_list = [{
                'manufacturer': 'SimManufacturer',
                'model': 'SimModel',
                'instrument_type': 'SimManufacturerSimModel',
                'serial': 'SimSerial',
                'address': 'SimModel',
                'id': 'SimManufacturerSimModel:SimSerial',
                'status': 'Ready'
            }]
            # no client_diagnostic.log posted in Simulated mode
            return inst_list
        logger.info("{} instrument(s) found".format(len(scopes)))
        inst_list = []
        for scope in scopes:
            try:
                i_dict = self._get_instrument_identity_dict(scope)
            except usb.core.USBError:
                pass  # logged in _get_instrument_identity_dict
            except socket.error:
                pass  # logged in _get_instrument_identity_dict
            else:
                inst_list.append(i_dict)
        self._update_states_file(inst_list)
        file_key = settings.GATEWAY_ID + '-diagnostic.log'
        logger.info("Transmitting diagnostic log")
        self.transmit_file(clogger.filepath, file_key=file_key)
        return inst_list

    def _update_states_file(self, inst_list):
        """Updates the states file with a list of instrument states

        Summary:
            Reads the instrument states file to check for a matching
            instrument to update the state for. If no matching
            instrument is found then the instrument data is added
            to the states list.

        Parameters:
            inst_list - a list of dictionaries of instrument states

        Returns:
            states - a list of instrument states including existing
            data that was not part of the inst_list to update them
        """
        states = self._read_instrument_states()
        new_insts = []
        for inst_data in inst_list:
            matches = [s for s in states if s['id'] == inst_data['id']]
            if matches:
                matches[0].update(inst_data)
            else:
                new_insts.append(inst_data)
        states.extend(new_insts)
        self._write_states_to_file(states)
        return states

    def _get_instrument_identity_dict(self, scope):
        """Gets the identity information from scope object

        Summary:
            Asks the ivi instrument object for its identity
            information. Also marks the status as Ready since
            the only way the identity information can be
            obtained is if the instrument is Ready to run,
            else an error would be raised.

        Parameters:
            scope: an ivi instrument object

        Returns:
            i_dict: a dictionary with manufacturer, model,
                instrument_type, serial, address (aka resource),
                id (aka instrument_type:serial), and the ivi
                object itself.
        """
        try:
            manf = scope.identity.instrument_manufacturer.title()
        # sometimes simply checking identity will trigger a USBError
        except usb.core.USBError:
            logger.warning("USBError in checking identity for: {}"
                           .format(scope))
            raise
        except socket.error:
            logger.warning("socket error in checking identity for: {}"
                           .format(scope))
            raise
        model = scope.identity.instrument_model
        instrument_type = settings.KNOWN_MANF_DICT[manf] + model
        serial = scope.identity.instrument_serial_number
        resource = scope.driver_operation.io_resource_descriptor
        if 'TCPIP::' in resource:
            address = resource.split('::')[1]
        else:
            address = resource
        i_dict = {
            'manufacturer': manf,
            'model': model,
            'instrument_type': instrument_type,
            'serial': serial,
            'resource': resource,
            'address': address,
            'id': instrument_type + ':' + serial,
            'status': 'Ready'
        }
        return i_dict

    def _handle_instructions(self):
        """Handles instructions from the server

        Handling depends on what level they are. At the most basic
        level, a command, this method writes the command to a file for
        the instrument client to pick up and process
        """
        instructions = self._get_server_instructions()
        # if no instructions at all, return early
        if not instructions:
            return
        self.instruction_id = instructions['id']
        info = self._validate_instruction_info(instructions)
        if instructions['level'] == 'Plan':
            self._handle_plan(info)
        elif instructions['level'] == 'Step':
            self._handle_step(info)
        elif instructions['level'] == 'Command':
            if 'command' in info:
                command = info['command']
            else:
                command = info
            # if not explicitly set in the command, use the
            # metadata from the instruction level
            if 'name' not in command:
                command['name'] = instructions['name']
            self._save_command(command)
        else:
            logger.info("unknown level, treating it as a command")
            self._save_command(info)

        # update the insructions to complete on the server
        logger.info("setting instruction {} to complete. The commands have "
                    "been saved on this machine".format(instructions['id']))
        _data = {"id": instructions['id'], 'status': 'complete'}
        self.put(INSTRUCT_URL, data=_data)
        self.instruction_id = None

    def _handle_plan(self, plan):
        for step in plan['steps']:
            self._handle_step(step)

    def _handle_step(self, step):
        if 'id' in step:
            logger.info("handling step %s" % step['id'])
        else:
            logger.info("handling step with no id")
        for command in step['commands']:
            self._save_command(command)

    def _save_command(self, command):
        """Adds the command to a command file to be run later.

        A separate process will pick up the command to run it,
        such as the ScopeClient's run_command method
        """
        logger.info("saving command {}".format(command['id']))
        self.update_command(command['id'], status='received')
        if os.path.exists(self.path_to_commands):
            logger.info("waiting for previous command to complete")
        # wait for the last command to be deleted.
        # stored in __current_command__
        command_timeout = 10 * 60 * 5  # 5 minute timeout per command
        counter = 0
        while os.path.exists(self.path_to_commands):
            time.sleep(0.1)
            counter += 1
            if counter > command_timeout:
                os.remove(self.path_to_commands)
        # write the new command to file with current data
        command["instruction_id"] = self.instruction_id
        command["start_datetime"] = str(datetime.datetime.now())
        with open(self.path_to_commands, 'w') as f:
            f.write(json.dumps(command))

    def _abort_command(self, command):
        if command and 'id' in command:
            self.update_command(command['id'], status='aborted')
        else:
            logger.debug("_abort_command() command has no 'id' to update "
                         "command status on the server")

    def _validate_command(self, command):
        """Validates the data in command

        Parameters:
            command: The command object must have an 'info' object,
            this info object must contain an 'instrument_type' string
            to indicate what instrument to use the command on.
        Returns:
            the command if it's valid
            None if found to be invalid
        """
        if not command:
            self._abort_command(command)
            return None
        if command['name'] == 'detect_instruments':
            command['info']['instrument_type'] = 'detecting'
            return command
        try:
            instrument_type = command['info']['instrument_type']
        except KeyError:
            logger.info("No instrument_type in info for command: {};"
                        "Aborting process_command".format(command))
            self._abort_command(command)
            return None
        else:
            logger.info("Validated command for {}".format(instrument_type))
            return command

    def _handle_command_file(self, command_file):
        tlogger.info("Reading command file")
        command = collections.defaultdict(str)
        try:
            with open(command_file, "r") as f:
                data = json.loads(f.read())
            command.update(data)
        except IOError as e:
            logger.debug("IOError reading command file: {}".format(e))
        except TypeError as e:
            # invalid JSON data in the file
            logger.warning("TypeError reading command file: {}"
                           .format(e))
        except Exception as e:
            logger.debug("Unexpected err reading command file {}"
                         .format(e))
        self._remove_command_file()
        self.command = self._validate_command(command)
        if self.command:
            tlogger.info("Command found in the command file, processing: {} "
                         "w/ id: {}".format(self.command['name'],
                                            self.command['id']))
            self.process_command()
        else:
            tlogger.warning("Invalid command found in command file")

    def _post_no_instruments(self):
        _data = {
            'id': settings.GATEWAY_ID,
            'status': "Online",  # gateway is still online
            'instruments': [],  # but no instruments
        }
        logger.info("Gateway _post_no_instruments %s" % _data)
        self.post(
            BASE_URL + "/gateway",
            headers=base.get_headers(),
            data=json.dumps(_data),
        )

    def _handle_detect_instruments_cmd(self):
        gateway_data = {
            'id': settings.GATEWAY_ID,
            'instruments': self._detect_instruments(),
            'status': 'Online',
        }
        self.put(BASE_URL + "/gateway", json.dumps(gateway_data))

    def _prepare_driver_for_trace(self, driver, trace_dict):
        """Prepares the driver for a trace dependent on command

        Summary:
            Looks up the method for preparing the trace depending on
            what type of trace command this is. Uses the Command.name
            to look up the appropriate method to prepare for trace.
            This will also decide what config_name is saved to the
            trace_dict, either the command id or the command arg.

        Returns:
            None. This method does not return a value.
        """
        simple_methods = {
            'Capture': self._prepare_capture,
            'Autoset': self._prepare_autoset,
            'Quickset': self._prepare_quickset,
        }
        if self.command['name'] in simple_methods:
            trace_dict['config_name'] = self.command['id']
            simple_methods[self.command['name']](driver, trace_dict)
        elif self.command['name'] == 'Config':
            trace_dict['config_name'] = self.config['name']
            driver.load_config()
        else:
            logger.warning("Unexpected command name " + self.command['name'])
            # sometimes a Command is named with a config's name
            logger.info("Running treating command like config and loading "
                        "attempting to load config with driver")
            trace_dict['config_name'] = self.command['name']
            driver.load_config()

    def fetch_trace_data(self, driver):
        logger.info("initiate measurement")
        driver.instr.measurement.initiate()
        self.timer.set_timeout(300)
        try:
            tlogger.info("Fetching waveform and measurement data")
            trace_dict = driver.fetch_measurements()
        except usb.core.USBError as e:
            logger.debug("USBError Fetching measurments")
            driver.handle_usb_error(e)
        except socket.error as e:
            logger.warning("Socket Error: {};".format(e))
            raise
        except FetchMeasurementError as e:
            self._handle_trace_error("FetchMeasurementError: Measurements "
                                     "Not Acquired Successfully")
        except Exception:
            logger.warning("fetch_measurements() error in fetch_trace_data")
            self.timer.clear_timeout()
            raise
        else:
            self.timer.clear_timeout()
            return trace_dict

    def get_metadata(self, driver):
        metadata = collections.defaultdict(str)
        metadata.update(driver.metadata)
        self.timer.set_timeout(120)

        # instrument fetch_setup dump
        # comment the following line out if raw setups start causing issues
        metadata['raw_setup'] = driver.fetch_raw_setup()

        # read instrument using ivi fields
        try:
            metadata['config_excerpt'] = driver.get_config_excerpt()
            logger.info("metadata config_excerpt is %s" % metadata['config_excerpt'])
        except Exception:
            logger.warning("post-trace fetch config exception", exc_info=True)
            metadata['config_excerpt'] = collections.defaultdict(str)
            metadata['config_excerpt']['channels'] = []

        try:
            channels = self._check_enabled_list_with_pods(
                enabled_list=metadata['config_excerpt']['channels'],
                driver=driver,
            )
        except Exception as e:
            logger.warning("exception checking channels with pods, e: {}"
                           .format(e))
        metadata['config_excerpt']['channels'] = channels

        try:
            if settings.SIMULATED:
                enabled_list = []

            else:
                enabled_list = self._check_enabled_list_with_pods(
                    enabled_list=metadata['config_excerpt']['enabled_list'],
                    driver=driver,
                )
        except Exception as e:
            logger.warning("exception checking enabled_list with pods, e: {}"
                           .format(e))
        metadata['config_excerpt']['enabled_list'] = enabled_list
        metadata['serial'] = self.serial

        self.timer.clear_timeout()
        driver.times['complete'] = time.time()
        driver.update_scorecard_times()
        return metadata

    def _check_channels_with_pods(self, channels, driver):
        pod_list = driver.pod1_list + driver.pod2_list
        checked_channels = []
        for channel in channels:
            if channel['name'] not in pod_list:
                checked_channels.append(channel)
        return checked_channels

    def _check_enabled_list_with_pods(self, enabled_list, driver):
        pod_list = driver.pod1_list + driver.pod2_list
        cleaned_list = []
        for channel_name in enabled_list:
            if channel_name not in pod_list:
                cleaned_list.append(channel_name)
        return cleaned_list

    def update_with_command_data(self, trace_dict):
        """Updates the trace_dict with the relevant command data

        Summary:
            Assigns the 'command' key/value in the trace_dict and
            also assigns important top level keys for the trace_dict
            from the command data.

        Returns:
            A dictionary with the trace_dict updated.
        """
        trace_dict['command'] = self.command
        keys = ['test_plan', 'id', 'g1_measurement', 'instrument_id',
                'user_id']
        for key in keys:
            if key in self.command:
                trace_dict[key] = self.command[key]
        trace_dict['instrument_type'] = self.command['info']['instrument_type']  # noqa
        trace_dict['command_id'] = self.command['id']
        return trace_dict

    def run_driver(self, driver):
        """Runs the setup on the instrument to get trace with measurments

        Called by get_trace(), this function processes driver to
        collect instrument data, including measurements, config, and
        other metadata. These make up a trace_dict that is passed to
        the Transmitter constructor.

        Parameters:
            driver: used to build a trace_dict for the Transmitter

        Returns:
            a Transmitter object to transmit the trace, or
            None if there is an error
        """
        if not driver:
            logger.error("No driver to process!")
            return
        self.command.update(driver.command)
        trace_dict = collections.defaultdict(str)
        self.config = driver.config
        logger.debug("config in setup is: %s" % self.config)
        # sets the ivi usb timeout if any interface is available
        if driver.instr._interface:
            driver.instr._interface.timeout = 25000

        tlogger.info("run_driver() loading config")
        self._prepare_driver_for_trace(driver, trace_dict)
        tlogger.info("Config loaded successfully")

        # fetch trace and related measurements
        trace_dict.update(self.fetch_trace_data(driver))

        # update with command info, with priority over driver
        trace_dict = self.update_with_command_data(trace_dict)

        # update with fetched trace metadata
        tlogger.info("Fetching post waveform data acquisition metadata")
        trace_dict['metadata'] = self.get_metadata(driver)
        return trace_dict

    def record_start(self):
        """Records the start of a command

        Summary:
            This updates the command to 'in progress' and updates the
            instrument to a 'Busy' status. The update_instrument_status
            call uses the local_only=True because the server update
            happens with the POST to commands by including the
            'instrument_status' in the payload.
        """
        if self.skip_http_reqs:
            logger.info("Local testing only. Skipping request to /commands")
            return
        payload = {}
        payload.update(self.command)
        if 'id' not in payload:
            logger.warning("missing id in command: {}".format(self.command))
        payload['status'] = 'in progress'
        payload['utilization'] = 'start'
        payload['instrument_status'] = 'Busy'
        # update the server's command and instrument status w/ one request
        url = BASE_URL + '/commands'
        self.put(url, data=json.dumps(payload))
        # update the local instrument states file
        self.update_instrument_status(status='Busy', local_only=True)

    def _update_states(self, states, new_state):
        """Updates the list of states with the data in new_state"""
        logger.info("updating instrument states...")
        # if it's a new state not with an asset id not in states
        if new_state['id'] not in [s['id'] for s in states]:
            # simply add it to the list of states and return them
            states.append(new_state)
            return states
        # otherwise check for a matching asset id and update the status
        for state in states:
            if new_state['id'] == state['id']:
                state['status'] = new_state['status']
        return states

    def _check_scope_acquisition_mode(self, instrument):
        """Checks the scopes settings for acquisition mode

        Checks acquisition type and responds to *IDN to check
        if the scope is working.
        """
        if settings.SIMULATED:
            return self._get_simulate_instrument_state()

        # set the defaults
        connection = "Unknown"  # need a way to check from instr object
        try:
            ivi_response = "Acquisition Type: " + instrument.acquisition.type
            high_level_status = "Ready"
        except Exception as e:
            logger.info(e)
            high_level_status = "Error"
            ivi_response = "Error"
        try:
            scipy_response = instrument._ask("*IDN?")
        except Exception as e:
            logger.info("Exception asking instrument *IDN, {}".format(e))
            scipy_response = "Error"
        state = {
            'status': high_level_status,
            'gradientone_api': ivi_response,
            'device_protocol': scipy_response,
            'connection': connection,
        }
        return state

    def _get_simulate_instrument_state(self, command_info={}):
        default_instrument_type = 'RigolDS1054Z'
        try:
            instrument_type = command_info['instrument_type']
        except (KeyError, TypeError):
            logger.info("Unable to read instrument_type from command...")
            logger.info("Marking state with default instrument type {}"
                        .format(default_instrument_type))
            instrument_type = default_instrument_type
        state = {
            'status': 'Ready',
            'gradientone_api': 'Acquisition Type: normal',
            'device_protocol': 'Ready',
            'connection': 'simulated',
            'instrument_type': instrument_type,
        }
        return state

    def _handle_gateway_diagnostic_command(self):
        """Handles an ad hoc diagnostic command

        The diagnostic command from the server is just an on-demand
        triggering of the same periodic update of the gateway instrument
        states. When update_scope_states is called, the
        client checks each instrument for the latest state of the instrument
        and makes a post to the server to update it with the latest
        information.
        """
        logger.info("_handle_gateway_diagnostic_command {}"
                    .format(self.command))
        if settings.SIMULATED:
            self.instrument_dicts = [{
                'instrument_type': 'RigolDS1054Z',
                'serial': 'DS1ZA192007095',
                'id': 'RigolDS1054Z:DS1ZA192007095',
                'address': 'TCPIP::169.254.2.70::INSTR',
                'status': 'Ready',
            }]
            self.states = self.instrument_dicts
            return
        if not self.instrument:
            self._post_no_instruments()
            self._write_states_to_file(self.states)
            return
        _data = {
            'id': settings.GATEWAY_ID,
            'name': settings.GATEWAY_ID,
            'company': settings.COMPANYNAME,
            'status': 'Online',  # gateway online, instrument status below
            'instruments': self._detect_instruments(),
        }
        logger.info("Gateway checking in with %s" % _data)
        self.post(
            BASE_URL + "/gateway",
            headers=base.get_headers(),
            data=json.dumps(_data),
        )
        data = {'id': self.command['id'], 'status': 'complete'}
        self.put(COMMAND_URL, data=json.dumps(data))

    def record_end(self):
        """Records the end of a command

        This marks the command as complete on the server and updates
        the instrument status to Ready.
        """
        # Called with local_only=False because we want to update the
        # server immediately that the asset is Ready
        self.update_instrument_status(status='Ready', local_only=False)

    def process_command(self):
        """Processes command data for instrument instance and command

        If necessary, instantiates instrument, then runs the command
        then saves the instrument used for the command to the class
        attribute. The command data is in the 'command' attribute
        """
        logger.debug("Processing command: %s" % self.command)
        logger.info("Processing command named: %s" % self.command['name'])
        self.record_start()
        self.run_command()
        self.record_end()
