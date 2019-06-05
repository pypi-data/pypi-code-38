'''
Worker module for Spreader
New Workers would create a subclass from here, and implement the required methods.
'''
from multiprocessing import Process, Queue, Lock
import abc
import datetime
import queue
import socket
from socket import timeout
import time

SPREADER_LOG_DEBUG = 0
SPREADER_LOG_MESSAGE = 1
SPREADER_LOG_WARNING = 2
SPREADER_LOG_ERROR = 3
SPREADER_LOG_FATAL = 4

SPREADER_WORKER_PING_LIMIT_IN_SECONDS = 180
SPREADER_WORKER_TIMEOUT_LIMIT_IN_SECONDS = 600

def encode_params(decoded_data: str) -> str:
    ''' Prepare data for Spreader Interop '''
    return decoded_data.replace('|', '&#124;').replace('\r\n', '&#13;&#10;')

def decode_params(encoded_data: str) -> str:
    ''' Decode Parameter data from Spreader Interop '''
    return encoded_data.replace('&#124;', '|').replace('&#13;&#10;', '\r\n')

def output_to_console(log_message):
    ''' Write a message to Console '''
    print(str.format('{} - {}', datetime.datetime.now(), log_message))

class SpreadWorker(abc.ABC):
    '''
    Main Worker Class
    '''

    # pylint: disable=too-many-instance-attributes

    def __init__(self, **kwargs):
        self.__transfer_lock = None
        self.__last_keep_alive = None
        self.__command_queue = Queue()
        self.__running = False
        self.debug_mode = False
        self.__registered_simple_scanners = []
        self.__job_parameters = ''
        self.__accesscodes = []
        self.job_params = {}
        self.__job_id = 0
        self.__client_init = False
        self.__last_start_attempt = None
        self.__new_task_event = ''

        if 'debug' in kwargs:
            self.debug_mode = kwargs['debug']
        if self.debug_mode:
            self.__log_debug('Debug Mode', False)

        if 'id' in kwargs:
            self.__worker_id = kwargs['id']
        else:
            raise Exception('You must specify a Worker ID.')

        self.__process = None

        if 'port' in kwargs:
            self.__port = int(kwargs['port'])
        else:
            self.__port = 21200

        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.settimeout(0.25)

        self.__log_debug(str.format('Worker ID = {}, Port = {}', self.__worker_id, self.__port), False)

    def __log_debug(self, log_string, log_to_client=True):
        ''' Log a Debug string to Console and Client '''
        if self.debug_mode:
            output_to_console(log_string)
            if log_to_client:
                self.__send_log_debug(log_string)

    def __log_message(self, log_string):
        ''' Log a Message to Console and Client '''
        output_to_console(log_string)
        self.__send_log_message(log_string)

    def __log_warning(self, log_string):
        ''' Log a Warning to Console and Client '''
        output_to_console(log_string)
        self.__send_log_warning(log_string)

    def __log_error(self, log_string):
        ''' Log an Error to Console and Client '''
        output_to_console(log_string)
        self.__send_log_error(log_string)

    def __log_fatal(self, log_string):
        ''' Log a Fatal message to Console and Client '''
        output_to_console(log_string)
        self.__send_log_fatal(log_string)

    def __repr__(self):
        return str.format('<SpreadWorker, WorkerID {}, Port {}>', self.__worker_id, self.__port)

    def __read_response(self):
        '''
        Locks any transfer opportunity until we get a response from the server.
        Only waits 5 seconds for a response, otherwise errors out.
        '''
        response = ''
        self.__log_debug('Acquiring Transfer Lock for Read Response...', False)
        with self.__transfer_lock:
            endtime = datetime.datetime.now() + datetime.timedelta(seconds=5)
            while datetime.datetime.now() < endtime:
                try:
                    data = self.__socket.recv(4096)
                    self.__log_debug(str.format('Found Response Data: {}', data), False)
                    data = data.decode().strip()
                    self.__log_debug(str.format('Returning Response Data: {}', data[9:]), False)
                    response = data[9:]
                    break
                except (timeout, BlockingIOError):
                    self.__log_debug('No Response Found yet. Waiting..', False)

        return response

    def __send_to_socket(self, command, data=''):
        self.__log_debug(str.format('Sending to socket, Command {}, Data {}', command, data), False)
        with self.__transfer_lock:
            output = command + '|' + self.__worker_id + '|' + data + '\r\n'
            self.__socket.send(output.encode())

    def __send_log(self, level, log_string):
        self.__send_to_socket('WKRLOG', str.format('{}|{}', level, encode_params(log_string)))

    def __send_log_debug(self, log_string):
        self.__send_log(SPREADER_LOG_DEBUG, log_string)

    def __send_log_message(self, log_string):
        self.__send_log(SPREADER_LOG_MESSAGE, log_string)

    def __send_log_warning(self, log_string):
        self.__send_log(SPREADER_LOG_WARNING, log_string)

    def __send_log_error(self, log_string):
        self.__send_log(SPREADER_LOG_ERROR, log_string)

    def __send_log_fatal(self, log_string):
        self.__send_log(SPREADER_LOG_FATAL, log_string)

    def __task_add_new(self, task_key, task_params, access_code):
        self.__send_to_socket('WKRTASKADD',
            str(self.__job_id) + '|' +
            encode_params(task_key) + '|' +
            encode_params(task_params) + '|' +
            encode_params(access_code))
        resp = self.__read_response()
        result = resp.split('|')[0]
        resp = resp.split('|')[1]
        if result == '0':
            resp = '0'

        return int(resp)

    def __send_worker_start(self):
        if self.__client_init:
            return

        if (not self.__last_start_attempt) or \
            ((datetime.datetime.now() - self.__last_start_attempt).total_seconds() > 10):
            self.__last_start_attempt = datetime.datetime.now()
            self.__log_debug('Client has not yet sent Initialization. Attempting to start.')
            self.__send_to_socket('WKRSTARTED')

    def __handle_client_ping(self):
        self.__send_to_socket('WKRPONG')

    def __handle_client_pong(self):
        self.__last_keep_alive = datetime.datetime.now()

    def __handle_client_init(self, params):
        self.__accesscodes = params.split('|')[0].split(';')
        self.__job_id = int(params.split('|')[1])
        self.__new_task_event = str.format('NEW_TASK_{}', self.__job_id)
        self.__job_parameters = decode_params(params.split('|')[2])
        self.do_init_jobparams()
        self.__client_init = True
        self.__send_to_socket('WKRINITIALIZED')
        self.__send_to_socket('WKREVENTSUBSCRIBE', self.__new_task_event)

    def __handle_client_task(self, task_data):
        datasplit = task_data.split('|')
        taskid = datasplit[0]
        params = datasplit[1]
        success = self.do_task(decode_params(params))

        self.__send_to_socket('WKRTASKDONE', str.format('{}|{}', taskid, 1 if success else 0))

    def __parse_queue_command(self, data):
        ''' Internal Queue Parser. '''
        try:
            tmpidx = data.index('|')
        except ValueError:
            tmpidx = 0

        if tmpidx > 0:
            command = data[:tmpidx]
            params = data[tmpidx + 1:]
        else:
            command = data
            params = ''

        if command == 'QUIT':
            self.__running = False
        elif command == 'DEBUG':
            self.__log_debug(params)
        elif command == 'MESSAGE':
            self.__log_message(params)
        elif command == 'WARNING':
            self.__log_warning(params)
        elif command == 'ERROR':
            self.__log_error(params)
        elif command == 'FATAL':
            self.__log_fatal(params)
        else:
            self.__log_debug(str.format('** Unknown Command: {}', command), False)

    def __parse_client_data(self, data):
        ''' Main Client Data Parser '''
        self.__log_debug(str.format('Received Client Data: {}', data), False)
        try:
            tmpidx = data.index('|')
        except ValueError:
            tmpidx = 0

        if tmpidx > 0:
            command = data[:tmpidx]
            params = data[tmpidx + 1:]
        else:
            command = data
            params = ''

        if command == 'WKRPING':
            self.__handle_client_ping()
        elif command == 'WKRTASK':
            self.__log_debug(str.format('Received a Task! Params: {}', params), False)
            self.__handle_client_task(params)
        elif command == 'WKRPONG':
            self.__handle_client_pong()
        elif command == 'WKRINIT':
            self.__handle_client_init(params)
        elif command == 'WKRSTOP':
            self.__log_debug('Received Stop. Quitting.', False)
            self.__running = False
        elif command == 'WKREVENT':
            self.__log_debug('Received Event: ' + params, False)
        else:
            self.__log_debug(str.format('Unknown Command {}, Quitting.', command), False)
            self.__running = False

    def __check_keep_alive(self):
        ''' Check to see if we've lost connection '''
        current = datetime.datetime.now()
        diff = current - self.__last_keep_alive
        diffinseconds = diff.total_seconds()
        if diffinseconds > SPREADER_WORKER_TIMEOUT_LIMIT_IN_SECONDS:
            self.__log_debug('Lost connection to Client', False)
        elif diffinseconds > SPREADER_WORKER_PING_LIMIT_IN_SECONDS:
            self.__send_to_socket('WKRPING')

    def __has_access(self, access_code):
        return access_code in self.__accesscodes

    def __do_scan(self):
        for idx in range(len(self.__registered_simple_scanners)):
            params = self.__registered_simple_scanners[idx]
            if (datetime.datetime.now() - params['last_run']).total_seconds() > params['loop_every']:
                params['method'](self, self.__job_parameters)
                params['last_run'] = datetime.datetime.now()

    def _command_loop(self, work_queue: Queue):
        ''' Method called by __process start/stop '''

        self.__log_debug('Connecting to Spreader Client via Localhost', False)
        self.__socket.connect(('localhost', self.__port))
        self.__transfer_lock = Lock()

        self.__last_keep_alive = datetime.datetime.now()

        self.__log_debug('Starting Command Loop.', False)
        while self.__running:
            if not self.__client_init:
                self.__send_worker_start()

            while not work_queue.empty():
                try:
                    n = work_queue.get(timeout=0.01)
                    self.__log_debug(str.format('Found Queue Item: {}', n), False)
                    self.__parse_queue_command(n)
                except queue.Empty:
                    self.__log_debug('Queue not empty, but no Queue item found. Waiting', False)

            try:
                with self.__transfer_lock:
                    data = self.__socket.recv(4096)
                self.__last_keep_alive = datetime.datetime.now()
                data = data.decode().strip()
                self.__parse_client_data(data)
            except (timeout, BlockingIOError):
                pass

            self.__check_keep_alive()

            if self.__has_access('SCAN'):
                self.__do_scan()

            time.sleep(0.25)
        self.__log_debug('** Command Loop Stopped.', False)

    def start(self):
        '''
        Start monitoring the Client for work
        '''
        if not self.__process:
            self.__running = True
            self.__process = Process(target=self._command_loop, args=(self.__command_queue,))
            self.__process.start()

    def wait_for_worker_close(self):
        '''
        Use this method in a Client implementation where you want to let the Worker dictate when to exit.
        WARNING: You will NOT be able to reclaim control until the main client disconnects the worker.
        '''
        if self.__process:
            self.__process.join()
            self.__client_init = False

    def stop(self):
        '''
        Adds a QUIT message to the __process queue, and waits for the process to stop
        '''
        if self.__process:
            self.__command_queue.put('QUIT')
            self.__process.join()
            self.__client_init = False

    def task_log_debug(self, log_message):
        '''
        Logs a debug message via the client.
        This is meant to be called by Subclassed workers implementing Task details.
        '''
        self.__log_debug(log_message)

    def task_log_message(self, log_message):
        '''
        Logs a message via the client.
        This is meant to be called by Subclassed workers implementing Task details.
        '''
        self.__log_message(log_message)

    def task_log_warning(self, log_message):
        '''
        Logs a warning message via the client.
        This is meant to be called by Subclassed workers implementing Task details.
        '''
        self.__log_warning(log_message)

    def task_log_error(self, log_message):
        '''
        Logs an error message via the client.
        This is meant to be called by Subclassed workers implementing Task details.
        '''
        self.__log_error(log_message)

    def task_log_fatal(self, log_message):
        '''
        Logs a fatal message via the client.
        This is meant to be called by Subclassed workers implementing Task details.
        '''
        self.__log_fatal(log_message)

    def task_add_new(self, task_key, task_params, access_code):
        '''
        Adds a new Task to the Spreader system, for consumption.
        This is meant to be called by Subclassed workers implementing Scanning.
        '''
        return self.__task_add_new(task_key, task_params, access_code)

    def log_debug(self, log_message):
        '''
        Adds a debug message to the Local Queue.
        This is meant to be called by processes External to the worker.
        '''
        self.__command_queue.put(str.format('DEBUG|{}', log_message))

    def log_message(self, log_message):
        '''
        Adds a message to the Local Queue.
        This is meant to be called by processes External to the worker.
        '''
        self.__command_queue.put(str.format('MESSAGE|{}', log_message))

    def log_warning(self, log_message):
        '''
        Adds a warning message to the Local Queue.
        This is meant to be called by processes External to the worker.
        '''
        self.__command_queue.put(str.format('WARNING|{}', log_message))

    def log_error(self, log_message):
        '''
        Adds an error message to the Local Queue.
        This is meant to be called by processes External to the worker.
        '''
        self.__command_queue.put(str.format('ERROR|{}', log_message))

    def log_fatal(self, log_message):
        '''
        Adds a fatal message to the Local Queue.
        This is meant to be called by processes External to the worker.
        '''
        self.__command_queue.put(str.format('FATAL|{}', log_message))

    def register_simple_scanner(self, scan_method, loop_frequency=5):
        '''
        Registers a Simple Scanner method.
        The worker will execute your method every [loop_frequency] seconds.
        scan_method should be a method with two parameters:
            An object representing a SpreadWorker
            A string, which will contain the parameters for the Job
        '''
        self.__registered_simple_scanners.append({'loop_every': loop_frequency,
            'method': scan_method,
            'last_run': datetime.datetime.now()})

    def do_init_jobparams(self):
        '''
        Fills the job_params dictionary with parameters.
        Default implementation fills this by splitting the params field with pipes.
        Feel free to reimplement this, and fill the dictionary however you'd prefer to edit your params!
        '''
        params = self.__job_parameters.split('|')

        for item in params:
            if item.strip() != '':
                tempitem = item.strip()
                self.job_params[tempitem[:tempitem.index('=')]] = tempitem[tempitem.index('=') + 1:]

    @abc.abstractmethod
    def do_task(self, task_params: str) -> bool:
        ''' Implement this method in your subclass to do the work! '''
        return False
