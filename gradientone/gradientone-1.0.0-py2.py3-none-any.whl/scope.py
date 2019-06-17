"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""

import base64
import collections
import json
import os
import os.path
import time
import gateway_helpers as helpers
import ivi_instruments
import command_runners
import settings
import socket
import sys
import usb
from ivi import ivi


# Read in config file info
COMPANYNAME = settings.COMPANYNAME
BASE_URL = settings.BASE_URL
TMPDIR = settings.TMPDIR
COMMAND_FILE = settings.COMMAND_FILE
STATES_FILE = settings.STATES_FILE
cfg = settings.cfg

DEFAULT_TEK_TYPE = 'TektronixMDO3012'
COMMAND_URL = BASE_URL + '/commands'
INSTRUCT_URL = BASE_URL + '/instructions.json'
SCPI_TIMEOUT = 120


# For Non-Sentry logging
logger = helpers.logger


class ScopeClient(command_runners.CommandRunner):
    """Manages sing scope client workflow"""

    def __init__(self, client_info, *args, **kwargs):
        super(ScopeClient, self).__init__(
            client_info=client_info, *args, **kwargs)
        self.name = client_info.identity_dict['id'] + '_client'
        self._init_instrument(client_info.identity_dict)
        cmdfilename = self.name + '_commands.json'
        self.path_to_commands = os.path.join(TMPDIR, cmdfilename)

    def _init_instrument(self, identity_dict):
        """Initializes instrument attribute from identity_dict

        Summary:
            Uses the instrument_type and resource from the identity_dict
            to look up the ivi instrument and instantiate the ivi
            object for sending commands.

        Parameters:
            identity_dict - dictionary containing identity information
                about the instrument. Must include instrument_type
                and resource

        Returns:
            instr - the ivi instrument object. This is just for
                convenience if the calling function wants to check,
                for existence of the instrument at the addresss.
                The instr object is assigned
                to the class attribute "instrument"

        Note:
            instr - the ivi instrument object - is in the "instrument"
                attribute
        """
        logger.info("Initializing instrument for ScopeClient w/ {}"
                    .format(identity_dict))
        i_type = identity_dict['instrument_type']
        resource = str(identity_dict['resource'])
        self.asset_id = identity_dict['id']
        self.instrument_type = identity_dict['instrument_type']
        self.serial = identity_dict['serial']
        self.identity_dict = identity_dict
        url = INSTRUCT_URL + '?next=t&instrument_id=' + self.asset_id
        self.instructions_url = url
        try:
            instr = ivi_instruments.IVI_INSTRUMENTS_DICT[i_type](resource)
        except ivi.NotInitializedException:
            logger.info("Instrument not initialized by ivi driver")
            raise
        except socket.error as e:
            logger.warning("Socket error {} in ScopeClient init instrument"
                           .format(e))
            raise
        except Exception as e:
            logger.warning("Unexpected exception %s" % e, exc_info=True)
            raise
        else:
            self.instrument = instr
        return instr   # return value not used.  should this be changed?

    def _record_instrument_state(self):
        state_dict = self._get_instrument_state(self.instrument)
        max_retries = 3
        retry_idx = 0
        self._update_states_file([state_dict])
        while (state_dict['status'] == 'Offline' or
               state_dict['status'] == 'SocketError' or
               state_dict['status'] == 'NotInitialized'):
            time.sleep(5)
            self._init_instrument(self.identity_dict)
            time.sleep(3)
            state_dict = self._get_instrument_state(self.instrument)
            retry_idx += 1
            self._update_states_file([state_dict])
            if retry_idx >= max_retries:
                break
        if (state_dict['status'] == 'Offline' or
            state_dict['status'] == 'SocketError' or
                state_dict['status'] == 'NotInitialized'):
            logger.info("Instrument Offline: {}".format(state_dict))
            logger.info("Exiting instrument client process")
            sys.exit(0)

    def run(self):
        """The main run method for the ScopeClient

        Summary:
            This method should be called when the ScopeClient process
            is started for a given connected instrument. The method
            will update the activity file for this client process,
            then updates the states file with the instrument's state.

            Most importantly, this method will check for commands
            for this instrument and if a command is found at the
            path for the command file then it will call the
            _handle_command_file method to handle the command.
        """
        act_idx = 0
        act_file_update_interval = 10
        state_update_idx = 0
        state_update_interval = 30
        self.update_activity_file()
        self._record_instrument_state()
        self._remove_command_file()  # remove any stale command files
        RUNTEST = False
        while True:
            if state_update_idx == state_update_interval:
                logger.info("ScopeClient recording instrument states")
                self._record_instrument_state()
                state_update_idx = 0
            if act_idx == act_file_update_interval:
                self.update_activity_file
                act_idx = 0
            self._handle_instructions()
            if settings.SIMULATED:
                self.instrument.apply_simulated_options()
            # check for any pending commands to start running
            if os.path.exists(self.path_to_commands):
                self._handle_command_file(self.path_to_commands)
            if RUNTEST:
                self._test_scpi_script_handling()
                RUNTEST = False
            time.sleep(1)
            state_update_idx += 1
            act_idx += 1

    def _test_scpi_script_handling(self):
        """unit test for the _handle_scpi_script method"""
        logger.info("TEST: testing scpi script handling")
        self.skip_http_reqs = True  # local test only
        sample_cmd = {
            "id": "C1378093611487504",  # sample command id
            "instrument_id": "TEST",
            "info": {
                "instrument_type": "RigolDS1054Z",
                "scpi_commands": [
                    {"method": "ask", "arg": "*ESR?"},
                    {"method": "write", "arg": ":waveform:format byte"}
                ],
                "comments": "Demo of scpi commands"
            }
        }
        logger.info("TEST: sample GradientOne command: {}".format(sample_cmd))
        expected_response = ["0", None]
        self.command = sample_cmd
        resp = self._handle_scpi_script()
        logger.info("TEST: script response: {}".format(resp))
        assert resp == expected_response
        logger.info("TEST: _test_scpi_script_handling PASSED!")
        self.skip_http_reqs = False  # restore normal operation after test

    def _handle_scpi_script(self):
        """Handles the GradientOne sending a SCPI script

        Summary:
            Sets the command in progress on the server. Then
            Iterates through each command in the scpi commands
            within the command['info']['scpi_commands'] list.
            Marks the command complete when finished and updates
            the command object with the results.

        Returns:
            results - the list of responses to the commands
        """
        scpi_commands = self.command['info']['scpi_commands']
        results = []
        for scpi_cmd in scpi_commands:
            try:
                response = self._handle_scpi_command(scpi_cmd)
            except helpers.TimeoutError:
                response = ("Command timed out after {} seconds"
                            .format(SCPI_TIMEOUT))
            # note if these raise scpi errors we should handle them
            except Exception as e:
                response = "Unexpected exception {}".format(e)
                logger.warning("Unexpected error with SCPI command",
                               exc_info=True)
            if response is None:
                response = "N/A"
            results.append(base64.encodestring(response))

        screenshot_url = ''
        if 'fetch_screenshot' in self.command['info']:
            if self.command['info']['fetch_screenshot']:
                screenshot_url = self._handle_scpi_screenshot()

        if self.skip_http_reqs:
            logger.info(
                "Local testing only. Skipping PUT request to /commands")
        else:
            cmd_data = {
                'id': self.command['id'],
                'status': 'complete',
                'results': results,
            }
            self.put(COMMAND_URL, data=json.dumps(cmd_data))
            data = {
                'command_id': self.command['id'],
                'config_name': self.command['arg'],
                'instrument_type': self.instrument_type,
                'info': {
                    'scpi_commands': scpi_commands,
                    'responses': results,
                },
                'screenshot_url': screenshot_url,
            }
            response = self.create_result(data)
        return results

    def _handle_scpi_screenshot(self):
        """Handles a screenshot command in scpi script"""
        screenshot_url = ''
        pngfile = None
        file_key = "screenshot-" + self.command['id'] + ".png"
        try:
            pngfile = self._fetch_screenshot_wrapper(file_key)
        except helpers.TimeoutError:
            msg = "Screenshot timed out"
            self._log_activity(msg, level='warning')
        except Exception as e:
            msg = "Screenshot unexpected exception: {}".format(e)
            self._log_activity(msg, level='error')
        else:
            screenshot_url = self._transmit_screenshot(pngfile, file_key)
        return screenshot_url

    def _transmit_screenshot(self, pngfile, file_key):
        """Transmits the screenshot and returls the screenshot url

        If the screenshot fails to transmit, returns and empty string
        """
        response = self.transmit_file(pngfile, file_key=file_key)
        if response:
            return BASE_URL + '/download?file_key=' + file_key
        else:
            return ''

    @helpers.timeout(5)
    def _fetch_screenshot_wrapper(self, file_key):
        png = self.instrument.display.fetch_screenshot()
        pngfile = os.path.join(TMPDIR, file_key)
        with open(pngfile, 'wb') as f:
            f.write(png)
        return pngfile

    def create_result(self, data):
        url = BASE_URL + "/results"
        return self.post(url, data=json.dumps({'result': data}))

    @helpers.timeout(SCPI_TIMEOUT)
    def _handle_scpi_command(self, scpi_cmd):
        """Passes the scpi command to the instrument

        Summary:
            Looks up the appropriate instrument method based on the
            value for 'method' in the scpi_cmd and then passes
            the value for 'arg' in scpi_cmd

        Parameters:
            scpi_cmd - dictionary object with the method and arg
                to send to the instrument

        Returns:
            response - the value that SCPI responds back with
        """
        logger.info("handling scpi command: {}".format(scpi_cmd))
        method_lookup = {
            'ask': self.instrument._ask,
            'read': self.instrument._read_raw,
            'write': self.instrument._write,
        }
        if scpi_cmd['method'] == 'read':
            # don't send arg
            response = method_lookup[scpi_cmd['method']]()
        else:
            response = method_lookup[scpi_cmd['method']]((scpi_cmd['arg']))
        logger.info("scpi command response: {}".format(response))
        return response

    def _get_instrument_type_from_scope(self, scope):
        try:
            manf = scope.identity.instrument_manufacturer.title()
        # sometimes simply checking identity will trigger a USBError
        except usb.core.USBError:
            raise
        model = scope.identity.instrument_model
        instrument_type = settings.KNOWN_MANF_DICT[manf] + model
        return instrument_type

    def _ask_instr(self, instrument, command_string, retry=True):
        try:
            return instrument._ask(command_string)
        except usb.core.USBError as e:
            logger.warning("USBError: {}; Consider resetting the USB device. "
                           "Either unplug the USB cable and plug in, or "
                           "try rebooting the device.".format(e))
            raise
        except ivi.NotInitializedException:
            logger.info("Instrument was not initialized. Calling initialize()")
            resource = instrument.driver_operation.io_resource_descriptor
            instrument.initialize(resource=resource)
            if retry:
                self._ask_instr(instrument, command_string, retry=False)
            else:
                raise
        except socket.error as e:
            logger.warning(
                "Socket error {} when asking: {}".format(e, command_string))
            code = instrument.close()
            logger.warning("instrument.close() returned {}".format(code))
            raise
        except Exception as e:
            logger.warning("Unexpected exception %s" % e, exc_info=True)
            raise

    def _refresh_instrument_instance(self, instrument):
        """Replaces the instrument instance with a new one

        Summary:
            The instrument passed as a parameter is used to find
            what kind of instrument instance is needed from the
            IVI_INSTRUMENTS_DICT, using the same instrument type
            and resource id.

        Returns:
            ivi instrument object, or None if instantation fails
        """
        time.sleep(3)
        i_type = self.instrument_type
        logger.info("Attempting to get new {} object".format(i_type))
        new_instr = None
        import ivi_instruments
        # This might be bad practice, but without it the client
        # will throw Usbtmc Exception("Device not found", 'init')
        # or a socket error, even if the device is working perfectly
        # normally after a power cycle. The error persists.
        # Thus far, the following try block is the ONLY way to get
        # the desired behaviour. Feel free to prove this wrong.
        resource = instrument.driver_operation.io_resource_descriptor
        try:
            new_instr = ivi_instruments.IVI_INSTRUMENTS_DICT[i_type](resource)
        except Exception as e:
            logger.warning("Unexpected Error after attempting to "
                           "obtain {} object: {}".format(i_type, e))
        # if new_instr was obtained, save over current one
        if new_instr:
            self.instrument = new_instr
        # note if new_instr None, this will return None
        return new_instr

    # question: is this method used?
    def _handle_instr_state_retry(self, instrument, instr_dict):
        """Returns a dict of instrument state"""
        new_instr = self._refresh_instrument_instance(instrument)
        # if we successfully got a new instrument instance and not None
        if new_instr:
            # get the state of the instrument and return
            return self._get_instrument_state(new_instr, retry=False)
        else:
            instr_dict["status"] = 'Offline'
            instr_dict['message'] = "Unabled to obtain new instrument instance"
            return instr_dict

    def _get_instrument_state(self, instrument, retry=True):
        instr_dict = collections.defaultdict(str)
        instr_dict.update(self.identity_dict)
        if settings.SIMULATED:
            instr_dict["status"] = "Ready"
            instr_dict["manufacturer"] = "Rigol"
            instr_dict["instrument_type"] = "RigolDS1054Z"
            instr_dict["model"] = "DS1054Z"
            instr_dict["serial"] = "941956"
            instr_dict["id"] = "RigolDS1054Z:941956"
            return instr_dict

        resp = None
        try:
            resp = self._ask_instr(instrument, "*ESR?")
        except usb.core.USBError as e:
            logger.warning("USBError when asking *ESR: {}".format(e))
            instr_dict["status"] = 'Offline'
            instr_dict['message'] = "USBError when checking instrument"
            return instr_dict
        except socket.error as e:
            # otherwise mark it Offline due to a Socket Error
            instr_dict["status"] = 'SocketError'
            message = "*ESR? returned a SocketError"
            instr_dict['message'] = message
            self._log_activity(
                message=message,
                level='warning',
                instrument_type=instr_dict['instrument_type']
            )
            return instr_dict
        # We need ivi.NotInitializedException because the instrument can be
        # closed and marked Offline due to being disconnected, but then
        # later get reconnected and so the actual instrument state is Online.
        # To handle this, we need initialize() to be called.
        except ivi.NotInitializedException:
            logger.info("Instrument was not initialized. Calling initialize()")
            resource = instrument.driver_operation.io_resource_descriptor
            instrument.initialize(resource=resource)
            instr_dict["status"] = 'NotInitialized'
            message = "Instrument was not initialized. Calling initialize()"
            instr_dict['message'] = message
            self._log_activity(
                message=message,
                level='warning',
                instrument_type=instr_dict['instrument_type']
            )
            return instr_dict
        except Exception as e:
            logger.warning(e, exc_info=True)
            msg = "Unexpected Error: Inaccessible {}".format(instrument)
            instr_dict['message'] = msg

        if resp is None:
            # don't even try getting identity of a nonresponsive instr
            instr_dict["status"] = 'Offline'
            logger.warning("instrument is nonresponsive")
            self._close_instrument(instrument)
            return instr_dict
        else:
            logger.info("*ESR response: {}".format(resp))

        try:
            resp = int(resp)
        except TypeError as e:
            # Will occur if instrument responds with None
            logger.warning(e, exc_info=True)
            msg = "Error: Instrument non-responsive {}".format(instrument)
            instr_dict['message'] = msg
            instr_dict['status'] = "Offline"
            self._close_instrument(instrument)
            return instr_dict

        if instr_dict["message"].find("Error") > -1:
            instr_dict["status"] = "Offline"
            logger.warning("*ESR Error: {}".format(instr_dict['message']))
            self._close_instrument(instrument)
            return instr_dict

        # If no errors occurred in checking state, then proceed to
        # Check the acquisition mode of the instrument and get
        # the identity information to send back the state
        instr_dict.update(self._check_scope_acquisition_mode(instrument))
        # Instrument is ready to be used
        instr_dict["status"] = "Ready"
        return instr_dict

    def _close_instrument(self, instrument=None):
        """Closes instrument instance and updates server

        The instrument is marked 'Offline' on the server
        """
        if instrument is None:
            instrument = self.instrument
        if not instrument:
            return
        try:
            instrument.close()
        # ToDo: identify and specify exceptions raised by close()
        except Exception as e:
            logger.info("Exception closing instrument. {}".format(e))
        self.identity_dict['status'] = 'Offline'
        del instrument
        self._update_instrument_state(self.identity_dict)


if __name__ == "__main__":
    print("hello from scope.py")
    scp = ScopeClient()
    scp.run()
