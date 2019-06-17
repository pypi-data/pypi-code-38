"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""

import collections
import datetime
import gzip
import json
import logging
import os
import re
import requests
import ssl
import subprocess
import sys
import traceback
from requests_toolbelt.multipart.encoder import MultipartEncoder
from shutil import copy
from settings import tryprint

try:
    from urllib.parse import urljoin
except:
    from urlparse import urljoin

import settings

os.environ['NO_PROXY'] = 'gradientone.com'
os.environ['no_proxy'] = 'gradientone.com'
HOME = settings.HOME
TMPDIR = settings.TMPDIR
COMMAND_FILE = settings.COMMAND_FILE
DATETIME_FORMAT = settings.DATETIME_FORMAT
BASE_URL = settings.BASE_URL
COMMAND_URL = settings.COMMAND_URL
DEFAULT_TEK_TYPE = settings.DEFAULT_TEK_TYPE
DEFAULT_LOGFILE = settings.DEFAULT_LOGFILE
ELIGIBLE_LOGFILE_SIZE = settings.ELIGIBLE_LOGFILE_SIZE
CLIENT_SETTINGS = settings.CLIENT_SETTINGS
COMMON_SETTINGS = settings.COMMON_SETTINGS
ARGS = settings.ARGS
try:
    LOGDIR = CLIENT_SETTINGS["LOGDIR"]
except:
    LOGDIR = os.path.join(HOME, 'logs')


def safe_write(filepath=None, content='', counter=0):
    """Writes the content to file, incrementing name if needed

    If unable to write to the filepath, a counter is incremented
    to try a new file up to the max number of tries at which point
    this function will abort and return early.

    Returns the filepath ultimately used, including the counter
    within the name if the counter was used.
    """
    counter += 1
    max_tries = 10
    if not filepath:
        tryprint("no filepath specified, cannot write ".format(content))
        return
    if counter > max_tries:
        tryprint("Max tries exceeded. Unable to write content: ".format(content))
        return
    if counter > 1:  # i.e. if it's not the first try
        filepath = filepath + "." + str(counter)
    try:
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath
    except Exception as e:
        tryprint("Error writing file. {}".format(e))
        return safe_write(filepath, content, counter)  # try again w/ new file


def cacert_path():
    ''' Look for a cacert.pem file in ~/etc.  If not
    checks other expected locations and copies to /etc
    before returning.
    '''
    etc = os.path.join(HOME, 'etc')
    certpath = os.path.join(etc, 'cacert.pem')
    if not os.access(certpath, os.R_OK):
        import certifi
        cacertsrc = certifi.where() # in development env
        if os.access(cacertsrc, os.R_OK):
            copy(cacertsrc, etc)
        else:
            # for deployments use dist/cacert.pem
            dist = os.path.join('.', os.getcwd())
            distcacert = os.path.join(dist, 'cacert.pem')
            copy(distcacert, etc)
    return os.path.join(etc, 'cacert.pem')


os.environ['REQUESTS_CA_BUNDLE'] = cacert_path()


def purge_logfile(file):
    if not os.path.isfile(file):
        return
    try:
        os.remove(file)
    except Exception:
        tryprint("Remove logfile exception")


def rotate_logfiles(original_file):
    for i in range(int(CLIENT_SETTINGS['MAX_NUM_LOGFILES'])):
        file_num = i + 1
        nextlogfile = original_file + "." + str(file_num)
        if not os.path.isfile(nextlogfile):
            break
        if os.stat(nextlogfile).st_size < int(ELIGIBLE_LOGFILE_SIZE):  # nopep8
            # purge the oldest file so that it's ready next rotate
            if file_num < int(CLIENT_SETTINGS['MAX_NUM_LOGFILES']):
                file_num += 1
                purge_logfile(original_file + "." + str(file_num))
            # break to return nextlogfile
            break
        # if all allowed files are full, purge and original
        if file_num == int(CLIENT_SETTINGS['MAX_NUM_LOGFILES']):
            purge_logfile(original_file)
            nextlogfile = original_file
    return nextlogfile


def get_logger(file_lvl=logging.DEBUG,
               filename='gradientone.log',
               console_lvl=logging.INFO,
               verbose=True,):
    """Returns the logger for client logs

    If verbose is True, the console will print debug level
    """
    loggername = str(os.getpid()) + '.' + filename
    _logger = logging.getLogger(loggername)

    # check if the logger already exists (avoids duplicate logs)
    if len(_logger.handlers) > 0:
        return _logger

    _logger.setLevel(logging.DEBUG)
    _logger.propagate = False

    if not os.path.exists(LOGDIR):
        try:
            os.makedirs(LOGDIR)
        except Exception as e:
            tryprint("Exception creating log directory, e: %s" % e)

    logger_file = os.path.join(LOGDIR, loggername)

    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    initmsg = now + " :: [ INIT ] initializing {}\n".format(loggername)
    # check if file exists
    if not os.path.isfile(logger_file):
        with open(logger_file, 'w') as f:
            f.write(initmsg)
    else:
        logger_file = safe_write(logger_file, initmsg)

    # check logfile size and rotate if needed
    if os.stat(logger_file).st_size > int(ELIGIBLE_LOGFILE_SIZE):
        logger_file = rotate_logfiles(logger_file)

    # create file handler
    console_handler = logging.StreamHandler()  # by default, sys.stderr
    file_handler = logging.FileHandler(logger_file)

    # check for command line verbosity level arg
    if sys.platform != 'win32':
        arg_lvl = ARGS.verbosity
    else:
        arg_lvl = None
    if not arg_lvl:
        pass
    elif arg_lvl == 'info':
        console_lvl = logging.INFO
    elif arg_lvl == 'debug':
        console_lvl = logging.DEBUG
    elif arg_lvl == 'warning':
        console_lvl = logging.WARNING
    elif arg_lvl == 'error':
        console_lvl = logging.ERROR
    else:
        tryprint("Ignoring command line arg: %s" % arg_lvl)
        tryprint("Using function arg: %s" % console_lvl)

    # set logging levels
    console_handler.setLevel(console_lvl)
    file_handler.setLevel(file_lvl)

    # create logging format
    formatter = logging.Formatter(
        '%(asctime)s :: [ %(levelname)s ] %(message)s',
        '%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Note verbose flag will set the console_lvl to the debug
    if verbose:
        console_handler.setLevel(logging.DEBUG)

    # only write to console on MacOS
    if sys.platform == "darwin":
        _logger.addHandler(console_handler)
    _logger.addHandler(file_handler)

    return _logger


logger = get_logger(filename='gradientone.log')


class DiagnosticLogger(object):

    def __init__(self, filename='diagnostic.log'):
        self.filename = filename
        self.filepath = os.path.join(LOGDIR, filename)
        self.dtfmt = '%Y-%m-%d %H:%M:%S'

    def refresh(self):
        """Refreshes the log, giving it a new init time"""
        now = datetime.datetime.now().strftime(self.dtfmt)
        initmsg = now + " :: [ INIT ] initializing {}\n".format(self.filename)
        with open(self.filepath, 'w') as f:
            f.write(initmsg)

    def write(self, message, *args):
        timestamp = datetime.datetime.now().strftime(self.dtfmt)
        statement = timestamp + " :: " + message
        tryprint(statement)
        statement = statement + "\n"
        with open(self.filepath, 'a') as f:
            f.write(statement)

    def debug(self, message, exc_info=False, *args):
        message = "[ DEBUG ] " + message
        if exc_info:
            message = message + traceback.format_exc()
        self.write(message)

    def info(self, message, exc_info=False, *args):
        message = "[ INFO ] " + message
        if exc_info:
            message = message + traceback.format_exc()
        self.write(message)

    def warning(self, message, exc_info=False, *args):
        message = "[ WARNING ] " + message
        if exc_info:
            message = message + traceback.format_exc()
        self.write(message)

    def error(self, message, exc_info=False, *args):
        message = "[ ERROR ] " + message
        if exc_info:
            message = message + traceback.format_exc()
        self.write(message)


t_diagnostic_logger = DiagnosticLogger(filename='trace_diagnostic.log')
c_diagnostic_logger = DiagnosticLogger(filename='client_diagnostic.log')


# on MacOS allow stdout and stderr to console for debugging
if sys.platform == "darwin":
    tryprint("Identified MacOS, printing stderr and stdout for debugging")
else:
    stdoutlog = os.path.join(LOGDIR, 'gstdout.log')
    sys.stdout = open(stdoutlog, 'w')
    stderrlog = os.path.join(LOGDIR, 'gstderr.log')
    sys.stderr = open(stderrlog, 'w')

AUTH_TOKEN = settings.AUTH_TOKEN
COMPANYNAME = settings.COMPANYNAME


def get_headers(refresh=False):
    auth_token = AUTH_TOKEN
    headers = {
        'Auth-Token': auth_token,
        'Company-Name': COMPANYNAME
    }
    url = BASE_URL + '/profile/auth_token/refresh'
    if refresh:
        try:
            headers['Refresh-Token'] = CLIENT_SETTINGS['REFRESH_TOKEN']
            response = requests.get(url, headers=headers)
            assert response.status_code == 200
            data = json.loads(response.text)
            headers['Auth-Token'] = data['new auth token']
            auth_token = data['new auth token']
        except Exception:
            logger.warning("Unable to get refresh token", exc_info=True)
    return headers


def get_usb_devices():
    """Returns list of all usb devices, including peripherals"""
    if sys.platform == 'win32' or sys.platform == 'darwin':
        return []  # no tested lsusb alternative yet
    device_re = re.compile(
        "Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)  # noqa
    df = subprocess.check_output("lsusb")
    devices = []
    for i in df.split('\n'):
        if i:
            info = device_re.match(i)
            if info:
                dinfo = info.groupdict()
                ptd = ('/dev/bus/usb/%s/%s'
                       % (dinfo.pop('bus'), dinfo.pop('device')))
                dinfo['path_to_device'] = ptd
                dinfo['usb_id'] = dinfo.pop('id')
                devices.append(dinfo)
    return devices


def get_copley_devices():
    """Returns a list of Copley devices
       may want to move this to a Copley module
    """
    if sys.platform == 'win32':
        return []
    if settings.DISABLE_DISCOVERY:
        return []
    dev_ports = os.listdir("/dev")
    copley_devices = []
    for dev_port in dev_ports:
        if dev_port.find("copleycan") == 0:
            # TODO: query the can device to find the full name
            inst_dict = {
                "manufacturer": "Copley",
                "product": "ADP-055-18",
                "instrument_type": "CopleyADP-055-18",
                "connection": os.path.join("/dev", dev_port)
            }
            copley_devices.append(inst_dict)
    # look in the list of ip devices
    ip_devices = [
        line.split(":")[1].strip()
        for line in subprocess.check_output(['ip', 'link']).split('\n')
        if line.find('    ') != 0 and len(line) > 0
    ]
    can_devices = [dev for dev in ip_devices if dev.find("can") == 0]
    for can_device in can_devices:
        inst_dict = {
            "manufacturer": "Copley",
            "product": "ADP-055-18",
            "instrument_type": "CopleyADP-055-18",
            "connection": can_device
        }
        copley_devices.append(inst_dict)
    return copley_devices


def binary_type(input):
    if int(sys.version[0]) < 3:
        return input
    else:
        return bytes(input, "utf-8")


class BaseClient(object):

    """Base client for methods common to all instruments"""

    def __init__(self, client_info=None, tags=[], name=''):
        self.session = requests.session()
        self.session.headers.update(get_headers())
        self.client_info = client_info
        self.states = []
        self.timer = Timer()
        try:
            self.activity_file = client_info.activity_file
        except:
            self.activity_file = None
        if not self.activity_file:
            self.activity_file = os.path.join(TMPDIR, 'client_activity.txt')
        self.name = name
        if name:
            self.name = name
        elif hasattr(client_info, 'name'):
            self.name = client_info.name
        else:
            self.name = 'client name not specified'

        self._is_unit_test = False
        self._is_integration_test = False
        self.command = collections.defaultdict(str)
        self.skip_http_reqs = False  # used for local testing

    @property
    def is_unit_test(self):
        """For testing client classes"""
        return self._is_unit_test

    @property
    def is_integration_test(self):
        """For testing client classes with server app"""
        return self._is_integration_test

    def update_activity_file(self):
        """Updates counter for nanny to check"""
        if not self.activity_file:
            activity_file = os.path.join(TMPDIR, self.name + '_activity.txt')
            self.activity_file = activity_file
            logger.warning(
                "Missing activity_file for client: {}; assiging {}"
                .format(self.name, self.activity_file)
            )
        content = datetime.datetime.now().strftime(DATETIME_FORMAT)
        self.activity_file = safe_write(self.activity_file, content)

    def update_commands(self, status="complete", message=""):
        if not self.command["id"]:
            logger.error("no id in command: %s" % self.command)
            return
        _data = {"id": self.command["id"], "status": status}
        if message:
            _data['message'] = message
        response = self.put(urljoin(BASE_URL, "/commands"),
                            data=json.dumps(_data))
        if os.path.exists(COMMAND_FILE):
            logger.info("updating commands in BaseClient")
            try:
                command = json.loads(open(COMMAND_FILE, "r"))
            except Exception as e:
                logger.debug(e, exc_info=True)
            i_url = BASE_URL + '/instructions.json'
            instruction_data = {
                'command_metadata': True,
                'command_id': self.command["id"],
                'instruction_id': command['instruction_id'],
                'duration': (datetime.datetime.now() -
                             command["start_datetime"]).total_seconds()
            }
            if 'result_id' in self.command:
                instruction_data['result_id'] = self.command['result_id']
            response = self.put(i_url, data=json.dumps(instruction_data))
            # delete the command file
            os.remove(COMMAND_FILE)
        else:
            logger.warning("no file %s" % COMMAND_FILE)

    def http_request(self, url, data=None, params=None, headers=None,
                     kind='get', retry=True):
        """Makes http requests to app engine

        retry - if True means 'yes, retry' for SSLErrors it will
            start a new session and recursively call http_request

        """
        self.session.headers = get_headers()
        if headers:
            self.session.headers.update(headers)
        if self.is_unit_test:
            logger.info("unit test http request to url: {}; "
                        "with headers: {}; data: {}; params: {};"
                        .format(url, headers, data, params))
            return DummyResponse()
        reqs = {
            'get': self.session.get,
            'post': self.session.post,
            'put': self.session.put,
            'del': self.session.delete,
        }
        if isinstance(data, dict):
            data = json.dumps(data)
        response = None

        # commented out because of noise, but if trying to debug
        # every single http request the client is making, including
        # GET requests every second for instructions, uncomment
        # the following line for a log statement
        # logger.debug("making %s request to url: %s" % (kind, url))

        try:
            if data:
                response = reqs[kind](url, data=data)
            else:
                response = reqs[kind](url, params=params)
            if response.status_code in [401, 403]:
                hdrs = get_headers(refresh=True)
                self.session.headers.update(hdrs)  # for refresh
                if headers:
                    self.session.headers.update(headers)  # method arg
                if data:
                    response = reqs[kind](url, data=data)
                else:
                    response = reqs[kind](url, params=params)
            if response.status_code != 200:
                logger.warning("response.text %s" % response.text)
                logger.warning("request headers %s" % self.session.headers)
                logger.info("request data in debug level")
                if data:
                    msg = "request data %s" % data
                else:
                    msg = "request params %s" % params
                if len(msg) > 500:
                    msg = msg[0:500] + "..."
                logger.debug(msg)
        except ssl.SSLError:
            logger.warning("SSLError!", exc_info=True)
            if retry:
                self.session = requests.session()
                response = self.http_request(url, data, params, headers, kind,
                                             retry=False)
            else:
                # if a retry was already attempted, don't retry forever
                logger.warning("Not retrying. Returning None")
        except Exception as e:
            logger.debug("request exc: %s" % e, exc_info=True)
        finally:
            self.session.headers = get_headers()  # reset the headers
            return response

    def post(self, url, data=None, headers=None):
        return self.http_request(url, data=data, headers=headers, kind='post')

    def put(self, url, data=None, headers=None):
        return self.http_request(url, data=data, headers=headers, kind='put')

    def get(self, url, params=None, headers=None):
        return self.http_request(url, params=params, headers=headers, kind='get')  # noqa

    def delete(self, url, params=None, headers=None):
        return self.http_request(url, params=params, headers=headers, kind='del')  # noqa

    def update_command(self, command_id, status):
        data = json.dumps({'command_id': command_id, 'status': status})
        try:
            response = self.put(COMMAND_URL, data=data)
        except Exception as e:
            logger.error("update_command() exc: %s" % e)

    def gzip_and_post_file(self, file, file_key='', command_id='',
                           category=''):
        gzip_file = file + '.gz'
        with open(file) as f_in, gzip.open(gzip_file, 'w') as f_out:
            if not file_key:
                file_key = os.path.basename(f_in.name)
            f_out.write(binary_type(f_in.read()))
        data_type = 'application/x-gzip'
        for element in [command_id, file_key, category]:
            if not isinstance(element, basestring):
                logger.error("element: %s is not a string, it is a: "
                             % (element, type(element)))

        multipartblob = MultipartEncoder(
            fields={
                'file': (file_key, open(gzip_file, 'r'), data_type),
                'command_id': str(command_id),
                'file_key': str(file_key),
                'category': category,
            }
        )
        try:
            blob_url = self.get(BASE_URL + "/upload/geturl")
            response = self.post(blob_url.text, data=multipartblob)
            assert response.status_code == 200
            logger.info("Uploaded file with file_key %s" % file_key)
            return response
        except Exception as e:
            logger.error("gzip_and_post_file() err %s" % e)

    def post_logfile(self, command_id=""):
        return
        # Commented out because log posts are timing out
        # logfile = logger.handlers[-1].baseFilename
        # if not os.path.isfile(logfile):
        #     logger.warning("Missing logfile!")
        #     return
        # self.transmit_file(logfile, command_id=command_id, category='logfile',
        #                    mode='r')

    def update_gateway_state(self, state={}, instruments=[]):
        """Updates the gateway state and instruments states

        state: dict of the gateway state
        instruments: list of instrument state dicts
        """
        url = BASE_URL + '/gateway'
        payload = {
            'state': {'pid': os.getpid()},
            'company': COMPANYNAME,
            'name': settings.GATEWAY_ID,
            'id': settings.GATEWAY_ID,
            'instruments': instruments,
        }
        logger.info("update_gateway_state with {}".format(payload))
        try:
            self.put(url, data=json.dumps(payload))
        except Exception as e:
            logger.debug(e, exc_info=True)

    def _read_instrument_states(self):
        """Reads instrument states from file"""
        states = []
        try:
            with open(settings.STATES_FILE, 'r') as f:
                states = json.loads(f.read())
        except IOError as e:
            # not able to read the file
            logger.warning("IOError _read_instrument_states(): {}".format(e))
        except TypeError as e:
            # bad data in the file
            logger.warning("TypeError _read_instrument_states(): {}".format(e))
        except Exception as e:
            logger.error("Unexpected error in _read_instrument_states(): {}"
                         .format(e))
        return states

    def _write_states_to_file(self, states=[]):
        logger.info("Writing states to file: {}; Data: {}"
                    .format(settings.STATES_FILE, states))
        try:
            with open(settings.STATES_FILE, 'w') as f:
                f.write(json.dumps(states))
        except IOError as e:
            # most likely not able to write to the file
            logger.warning("IOError _write_states_to_file(): {}".format(e))
        except TypeError as e:
            # most likely bad data in states
            logger.warning("TypeError _write_states_to_file(): {}".format(e))
        except Exception as e:
            logger.error("Unexpected error in _write_states_to_file(): {}"
                         .format(e))

    def _update_instrument_state(self, instr_dict):
        self.update_gateway_state(instruments=[instr_dict])

    def transmit_file(self, filepath, file_key='', command_id='', category='',
                      mode='rb'):
        """transmits file to blobstore

        - assumes the file is already gzipped
        - deletes the local file after successfully transmitting
        """
        with open(filepath, mode) as f:
            filename = os.path.basename(f.name)
        if not file_key:
            file_key = filename
        fields = {
            'file': (filename, open(filepath, mode)),
            'file_key': file_key,
        }
        if command_id:
            fields['command_id'] = command_id
        if category:
            fields['category'] = category
        multipartblob = MultipartEncoder(
            fields=fields
        )
        resp = self.get(BASE_URL + "/upload/geturl")
        headers = {'Content-Type': multipartblob.content_type}
        response = None
        try:
            response = requests.post(resp.text, data=multipartblob,
                                     headers=headers)
        except TypeError as e:
            logger.warning("TypeError during transmit_file call",
                           exc_info=True)
        except ssl.SSLError:
            logger.warning("SSLError! during transmit_file",
                           exc_info=True)
        # log the response before returning
        if response.status_code == 200:
            logger.info("File upload for %s succeeded!" % filename)
        else:
            logger.info("File upload for %s failed" % filename)
            response_text = None
            if hasattr(response, 'text'):
                response_text = response.text
            if not response_text:
                logger.info("No transmit_file response text to log")
            else:
                logger.info("transmit_file response: %s" % response_text)
        return response

    def remove_file(self, filepath):
        try:
            os.remove(filepath)
        except:
            logger.debug("Exception while removing file")

    def _log_activity(self, message, level="info", exc_info=False,
                      data={}, instrument_type=''):
        """Logs activity both locally and to server

        Parameters:
            message - string summarizing the activity
            level - string indicating log level
            exc_info - boolean for exc_info kwarg for logging
            data - dictionary for more detail about the activity
            instrument_type - the instrument_type of the instrument
                that triggered the activity
        """
        log_funcs = {
            'debug': logger.debug,
            'info': logger.info,
            'warning': logger.warning,
            'error': logger.error,
        }
        # log it locally
        log_funcs[level](message, exc_info=exc_info)
        # post the activity to the server
        activity = {
            'level': level,
            'message': message,
            'data': data,
        }
        if self.command and 'id' in self.command:
            activity['command_id'] = self.command['id']
        if instrument_type:
            activity['instrument_type'] = instrument_type
        self.post(BASE_URL + '/activity', data=json.dumps(activity))


class Timer(object):

    def signal_handler(self, signum, frame):
        raise Exception("Timeouts: Timed out!")

    def set_timeout(self, seconds=10):
        pass
        # ToDo: Implement for windows
        # signal.signal(signal.SIGALRM, self.signal_handler)
        # signal.alarm(seconds)

    def clear_timeout(self):
        pass


class DummyResponse(object):

    def __init__(self, *args, **kwargs):
        self._text = json.dumps({'message': "DummyResponse text"})
        self._status_code = 200

    @property
    def text(self):
        return self._text

    @property
    def status_code(self):
        return self._status_code


class GradientOneError(Exception):
    """docstring for GradientOne"""
    def __init__(self, message='', *args, **kwargs):
        super(GradientOneError, self).__init__(message, *args, **kwargs)
        self.message = message
        self.write_to_file()

    def write_to_file(self):
        try:
            with open(settings.ERROR_FILE, 'w') as f:
                f.write(self.message)
        except IOError as e:
            # not able to read the file
            logger.warning("IOError in GradientOneError(): {}".format(e))
        except TypeError as e:
            # bad data in the file
            logger.warning("TypeError in GradientOneError(): {}".format(e))
        except Exception as e:
            logger.error("Unexpected err in GradientOneError(): {}".format(e))


class InstrumentInstructionError(GradientOneError):
    pass


class ReadSettingsError(GradientOneError):
    def __init__(self, kind='', *args, **kwargs):
        msg = "Capture Failed, Unable To Get Instrument Settings"
        logger.info("ReadSettingsError: {}".format(kind))
        super(ReadSettingsError, self).__init__(message=msg, *args, **kwargs)


class WriteSettingsError(GradientOneError):
    def __init__(self, kind='', *args, **kwargs):
        msg = "Capture Failed, Unable To Configure Instrument Settings"
        logger.info("WriteSettingsError: {}".format(kind))
        super(WriteSettingsError, self).__init__(message=msg, *args, **kwargs)


class FetchWaveformError(GradientOneError):
    def __init__(self, kind='', *args, **kwargs):
        msg = "Capture Failed, No Waveform Acquired. Confirm Setup and Try Again"
        logger.info("FetchWaveformError: {}".format(kind))
        super(FetchWaveformError, self).__init__(message=msg, *args, **kwargs)


class FetchMeasurementError(GradientOneError):
    def __init__(self, kind='', *args, **kwargs):
        msg = "Measurements Not Acquired Successfully"
        logger.info("FetchMeasurementError: {}".format(kind))
        super(FetchMeasurementError, self).__init__(message=msg, *args, **kwargs)


class FetchRawSetupError(GradientOneError):
    def __init__(self, kind='', *args, **kwargs):
        msg = "Raw Setup Not Acquired Successfully"
        logger.info("FetchRawSetupError: {}".format(kind))
        super(FetchRawSetupError, self).__init__(message=msg, *args, **kwargs)


class FetchScreenshotError(GradientOneError):
    def __init__(self, kind='', *args, **kwargs):
        msg = "Screenshot Not Acquired Successfully"
        logger.info("FetchScreenshotError: {}".format(kind))
        super(FetchScreenshotError, self).__init__(message=msg, *args, **kwargs)
