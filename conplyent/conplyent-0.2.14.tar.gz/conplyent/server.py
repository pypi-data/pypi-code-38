'''
:File: server.py
:Author: Jayesh Joshi
:Email: jayeshjo1@utexas.edu
'''

import os
import sys
from glob import glob
from functools import wraps
from shutil import rmtree
from threading import Thread
from zmq import Again, ZMQError
from queue import Queue
from pathlib import Path

from ._zmq_pair import ZMQPair
from ._msg import MSGType, MSG
from ._general import SynchronizedDict, logger, os_name
from .exceptions import min_exception_to_str, ConsoleExecTimeout, exception_to_str
from .console import ConsoleExecutor


MSG_PORT = {}  # contains a dict of function names and calls
JOBS = SynchronizedDict()  # contains a dict of jobs and their
_msg_num = {}  # Ensures that MSG queue in client can be properly ordered

# Default exit codes
INVALID_PARAMETER = -1
SUCCESS = 0
ERROR = 1

# Default Exec queue params
INPUT = 0
KILL = 1

# Job indexes
QUEUE_IDX = 0
THREAD_IDX = 1


def start(port=9922):
    '''
    Begins the server on the current process. This is a looped call and only
    exists on KeyboardInterrupt  or if a connected client has requested to close
    the server.

    This is a wrapper aorund the ZMQ library using the PAIR method to
    communicate with the client. This binds the socket to localhost and port
    specified and will continually listen to the port for any activity.
    Initially, the client should begin by establishing the connection and
    performing a handshake to ensure that server is alive. This is done within
    the ZMQPair class and this method doesn't need to worry about it.

    Once the connection has been established, this method will continually
    listen for any requests from the client. Requests available are broken into
    three categories: heartbeat, sync, and command. Heartbeat, also handled
    within ZMQPair, simply responds back to the client to let the client know
    that the server is alive and able to communicate. Sync lets the client know
    which commands are registered and able for client to run (more on this
    later). Commands allows the client to access any registered method which
    the server can begin executing. When the server receives a command, it will
    immediately respond with an acknowledge to let the client know that the
    message has been received. Then, will continue executing the command. These
    commands can be foreground or background commands. Many commands can be
    performed in the foreground if they are not IO bound. For background tasks,
    server will update the client letting them know what job number has been
    assigned to this task so the client can receive messages and sort them out.
    There are also registered methods that can interact with the background
    tasks to affect their runtime.

    Finally, for the pre-defined registered method of "close_server", the server
    will update the client as per the method definition and then gracefully
    exit.

    :param port: Port to listen to in localhost.
    :type port: int

    :returns: SUCCESS if exiting gracefully.
    '''
    global _zmq_pair

    _zmq_pair = ZMQPair(port=port)
    _zmq_pair.bind()
    logger.info("SERVER START:: Begin listening on port {}".format(port))
    idx = 0

    while(True):
        msg = _zmq_pair.recv_msg()
        try:
            if(msg.type == MSGType.COMMAND):
                _zmq_pair.send_msg(MSG(MSGType.ACKNOWLEDGE, request_id=idx))
                MSG_PORT[msg.cmd_id](idx, *msg.args, **msg.kwargs)
                if(msg.cmd_id == "close_server"):
                    _zmq_pair.close()
                    return SUCCESS
                idx = (idx + 1) % 0xFFFFFFFF  # I really hope noone creates more than 4 mil jobs at once...
            elif(msg.type == MSGType.SYNC):
                _zmq_pair.send_msg(MSG(MSGType.SYNC, args=(list(MSG_PORT.keys()),)))
        except KeyboardInterrupt:
            _zmq_pair.close()  # make sure we close zmq gracefully before exit
            raise
        except Again:
            logger.info("Lost connection with host...")
        except Exception:
            logger.info(exception_to_str())


def register_command(func):
    '''
    Decorator that registers the underlying function as a registered
    command that clients can execute remotely. This registration is used by the
    server to determine available commands.

    The wrapper will initially update the client and echo the request. Then,
    will execute the method and retrive the exit code. If there was an exception
    from the function, the wrapper will inform the client of the error and
    update the exit code to ERROR (1). Finally, the wrapper will report the
    completion of the function to the client reporting the exit code
    (INVALID_PARAMETER = -1, SUCCESS = 0, ERROR = 1).

    This module defines several commands that are available by default. Users
    can develop their own custom server commands using this decorator or even
    choose to clear default commands by clearing MSG_PORT if they so wish.

    By default this will provide the commands as accessible by their function
    name but am considering possibly allowing users to specify a name. (simple
    but need to create a few asserts to ensure it's a valid name <<).

    The functions that are registered under the server require that the first
    argument be idx. Idx refers to the job number that will be assigned once
    the function is called. This is important in updating the client to
    ensure that we are able to communicate to the client with the proper job
    number.

    From within the function, users can use calls to
    :meth:`server.update_client` to update the client with any output.

    .. note:: These functions will not include the idx in their docstring cuz
        it would be super redundant and don't help in their explanation
    '''
    function_name = func.__name__

    @wraps(func)
    def register_wrapper(idx, *args, **kwargs):
        request = "{} {} {}".format(function_name, args, kwargs)
        logger.info("Job {}: {}".format(idx, request))
        update_client(idx, request)

        try:
            exit_code = func(idx, *args, **kwargs)
        except Again:
            logger.info("Lost connection with host...")
            return
        except Exception:
            update_client(idx, min_exception_to_str())
            exit_code = 1
        _zmq_pair.send_msg(MSG(MSGType.COMPLETE, request_id=idx, exit_code=exit_code, msg_num=_msg_num[idx]))

    MSG_PORT[function_name] = register_wrapper
    return register_wrapper


def register_background_command(func):
    '''
    Decorator that registers the underlying function as a registered
    command that clients can execute remotely. This function will be executed on
    a background thread with a python Queue established between the main thread
    and the background thread for communication. These background commands are
    useful for functions that are IO bound or for those that will take longer
    than a few instructions (to prevent the server from blocking). Finally,
    these threads are ran as 'daemon' so exits alongside the server if the
    server prematurely exits.

    These background commands follow similar wrapper pattern to
    :meth:`server.register_command` in their exit code and error handling. These
    functions must return an exit code but do not need to worry about pre- and
    post- handling. Unlike the regular register_command decorator, this wrapper
    will add the command call to the JOBS dictionary as an active job which
    can be used for communcation using other commands.

    The function must have idx, and queue as their first two arguments.
    See register_command for details on idx, and how to update the client with
    output. Queue is used to communicate between the main server thread and
    these background threads if they require such communication. I.e. if we want
    to implement commands that require the thread's response. For default
    commands provided by conplyent, the queue and thread objects can be accessed
    through JOBS dict. This dict is accessible by providing job number as key
    and a tuple using QUEUE_IDX and THREAD_IDX to access the queue and thread
    objects respectively. The default queue recognition is by providing a
    dictionary that specifies "type" as either INPUT or KILL, and "value" if
    necessary. If developers chooses to create their own functions, they can
    redefine this queue as they see fit.

    .. note:: These functions will not include the idx or queue in their
        docstring cuz it would be super redundant and don't help in their
        explanation
    '''
    function_name = func.__name__

    def bg_server(idx, args, kwargs):
        request = "{} {} {}".format(function_name, args[1:], kwargs)
        logger.info("Job {} BG: {}".format(idx, request))
        update_client(idx, request)
        try:
            try:
                exit_code = func(idx, *args, **kwargs)
            except Again:
                logger.info("Lost connection with host...")
                JOBS[idx] = None
                return
            except Exception:
                update_client(idx, min_exception_to_str())
                exit_code = ERROR

            _zmq_pair.send_msg(MSG(MSGType.COMPLETE, request_id=idx, exit_code=exit_code, msg_num=_msg_num[idx]))
        except ZMQError:
            pass  # Client may have disconnected
        JOBS[idx] = None

    @wraps(func)
    def register_wrapper(idx, *args, **kwargs):
        io_pipe_r, io_pipe_w = os.pipe()
        my_queue = Queue()
        args = (my_queue,) + args
        t = Thread(target=bg_server, args=(idx, args, kwargs,), daemon=True)
        JOBS[idx] = (my_queue, t, args[1:], kwargs)
        t.start()

    MSG_PORT[function_name] = register_wrapper
    return register_wrapper


def update_client(idx, string):
    '''
    Sends the string to the client with the attached index to allow client to
    link messages to jobs. The string is sent as a pickled message object
    and doesn't have a upper limit on how long it could be. But y'know, better
    practice to put a limit on it. Sending huge messages over the network will
    eventually put a lower priority on the task by Windows (unless running in
    server environment.) This limit is pretty high though so for regular
    applications, users shouldn't worry.

    Note: this should never contain the exit code. Exit code will automatically
    sent by the wrapper.

    :param idx: Job number assigned by the server for this task.
    :type idx: int
    :param string: Message to send to the server as an update.
    :type string: str
    '''
    try:
        _msg_num.setdefault(idx, 0)
        _zmq_pair.send_msg(MSG(MSGType.DETAILS, request_id=idx, details=string, msg_num=_msg_num[idx]))
        _msg_num[idx] += 1
    except Again:
        logger.info("Failed to contact client...")
        raise


@register_command
def cd(idx, dest):
    '''
    Call os.chdir to be able to change current working directory of the server.
    If successful, will echo the new working directory back to the user and
    return SUCCESS exit code. Otherwise, will report to the user that server
    couldn't find the said directory and return INVALID_PARAM exit code.

    :param dest: Destination directory. Limitations for these are the same
        as os.chdir, in that it could be relative path or absolute. I.e.
        will support ".." to go backwards relatively or "/" to start at the
        root of this directory.
    :type dest: str

    :returns: SUCCESS if able to change directory. INVALID_PARAMETER if
        directory requested does not exist
    '''
    os.chdir(dest)
    update_client(idx, os.getcwd())
    return SUCCESS


@register_command
def ls(idx, src="."):
    '''
    Updates the client with the listing of the directory. This function
    currently only takes in a single parameter: src. If the user specifies the
    source to list, then ls will output the directory listing from there.
    Otherwise uses the current working directory. This display will specify
    whether the file found is a directory, file or a link and show the files
    in that order. If user provides a path and it doesn't exist as a directory,
    then will return INVALID_PARAM and let user know that directory does not
    exist. Otherwise, will return user with the listing of the directory and
    exit with SUCCESS.

    Future considerations -- expand it to show more details similar to BASH.

    :param src: Source path to list directory. Default cwd.
    :type src: str

    :returns: SUCCESS if able to list directory. INVALID_PARAMETER if directory
        requested does not exist
    '''
    if(not(os.path.isdir(src))):
        update_client(idx, "{}: No such directory".format(src))
        return INVALID_PARAMETER
    dir_path = os.getcwd() if src == "." else src
    name_list = "Listing of Directory {}:\n\n".format(dir_path)
    dir_list = []
    link_list = []
    file_list = []
    for file in glob("{}/*".format(dir_path)):
        file = os.path.basename(file)
        if(os.path.isdir(file)):
            dir_list.append(file)
        elif(os.path.islink(file)):
            link_list.append(file)
        else:
            file_list.append(file)
    name_list += "\n".join(["d {}".format(i) for i in dir_list]) + "".join(["\nf {}".format(i) for i in file_list]) +\
        "".join(["\nl {}".format(i) for i in link_list])
    update_client(idx, name_list)
    return SUCCESS


@register_command
def cwd(idx):
    '''
    Updates the client with the current working directory of the server.

    :returns: SUCCESS -- should never fail...
    '''
    update_client(idx, os.getcwd())
    return SUCCESS


@register_command
def mkdir(idx, path, mode=None):
    '''
    Creates a new empty directory under the path provided by the user. If the
    path exists, either as a file or a directory, then update the client that
    the path already exists and return INVALID_PARAMETER. Otherwise, create a
    directory and update the user that the directory has been created.

    Users may also pass in mode as either an argument or kwarg to pass into
    os.mkdir to change the mode of the file created. If the mode passed in is
    rejected by os.mkdir, server will report to the client of the error.

    :param path: Path of new directory to be created.
    :type path: str

    :Optional:

    :param mode: Mode of the directories to be created.
    :type mode: int

    :returns: SUCCESS if able to create a directory. INVALID_PARAMETER if there
        exists something in the path.
    '''
    if(not(os.path.exists(path))):
        if(mode is None):
            os.mkdir(path)
        else:
            os.mkdir(path, mode)
        update_client(idx, "Created directory: {}".format(path))
        return SUCCESS
    else:
        update_client(idx, "Directory or File {} already exists".format(path))
        return INVALID_PARAMETER


@register_command
def mkdirs(idx, path, exist_ok=False):
    '''
    Goes through the whole path, creating directories if they don't exist. By
    default, this will throw an error if the end directory already exists. Users
    can pass in exist_ok to prevent this error.

    :param path: Path of new directory to be created
    :type path: str

    :Optional:

    :param exist_ok: set to True if not to throw error if exists
    :type exist_ok: bool

    :returns: SUCCESS
    '''
    Path(path).mkdir(parents=True, exist_ok=exist_ok)
    update_client(idx, "Created directory: {}".format(path))
    return SUCCESS


@register_command
def rm(idx, path, recursive=False):
    '''
    Removes files or directories or links within the path specified. Initially,
    will check to see if anything exists in the path. If it doesn't then report
    to the client that there is nothing to be removed in the path provided and
    return INVALID_PARAMETER. Otherwise, if the path points to a file or link,
    then remove it, update the client and return SUCCESS. If the path points to
    a directory, then check if the directory has any contents within it. If it
    doesn't then we can safely remove it and update the client + return SUCCESS.
    Otherwise, remove the directory and all of its content if user has passed in
    recursive, update the cleint + return SUCCESS. If the client didn't specify
    recursive (or noted to not do recursive), then let the client know that the
    directory is not empty and return INVALID_PARAMETER.

    :param path: Path of file/directory to remove.
    :type path: str

    :Optional:

    :param recursive: True if we should remove all contents within a directory.
        False to exit if directory contains anything.
    :type recursive: bool

    :returns: SUCCESS if able to remove successfully. INVALID_PARAMETER if no
        file/directory exists in the path or recursive is False and path
        contains a non-empty directory.
    '''
    if(os.path.exists(path)):
        if((os.path.isdir(path) and recursive) or (os.path.isdir(path) and not(os.listdir(path)))):
            rmtree(path)
            update_client(idx, "Removed directory {}".format(path))
            return SUCCESS
        elif(not(os.path.isdir(path))):
            os.remove(path)
            update_client(idx, "Removed file {}".format(path))
            return SUCCESS
        else:
            update_client(idx, "Non-Empty Directory... Pass recursive to recursivly remove directory")
            return INVALID_PARAMETER
    else:
        update_client(idx, "Directory or File {} doesn't exist?".format(path))
        return INVALID_PARAMETER


@register_command
def rdfile(idx, path, limit=1024):
    '''
    Opens file in the path that the user provided and reads it contents. First,
    this function will echo "Contents of {path provided by user} and updates
    the user for each KB of data in the file contained. This data is sent as
    binary and left to the client to decode as necessary. Once complete, will
    will return SUCCESS. If the path doesn't point to a file, then will inform
    the client and return INVALID_PARAMETER.

    :param path: Path to file to read.
    :type path: str

    :Optional:

    :param limit: Number in bytes to send per transaction. This is default 1 KB.
        Higher numbers may slow down network and increase the chances of packet
        loss.
    :type limit: int

    :returns: SUCCESS if able to read the file. INVALID_PARAM if file doesn't
        exist.
    '''
    if(os.path.exists(path) and not(os.path.isdir(path))):
        with open(path, 'rb') as file:
            update_client(idx, "Contents of {}".format(path))
            while(True):
                chunk = file.read(limit)
                if(chunk):
                    update_client(idx, chunk)
                else:
                    break
        return SUCCESS
    else:
        update_client(idx, "Unknown file: {}".format(path))
        return INVALID_PARAMETER


@register_command
def wrfile(idx, path, data, append=False):
    '''
    Opens file in path for write and flushes the data provided. This data must
    be in binary and the file must exist in path. By default this will create a
    new file decriptor under the name provided and flush the data. This would
    mean that if the file exists, then this call would delete the old file and
    add the data provided. Users can bypass this by providing append=True to
    append to the end of file instead.

    This call will check to see if the path exists as a directory, in which case
    this will notify the client and return INVALID_PARAMETER. Otherwise, will
    begin to write all of the data, let the user know of completion and return
    SUCCESS. This may also throw an error if the input provided by the user
    is not writable.

    :param path: Path to file to write
    :type path: str
    :param data: Data in bytes to write to file
    :type data: bytes

    :Optional:

    :param append: True to append to end of file if file exists. False default.
    :type append: bool

    :returns: SUCCESS if able to write into file. INVALID_PARAMETER if path
        exists as a directory.
    '''
    if(os.path.exists(path) and os.path.isdir(path)):
        update_client(idx, "wrfile: Path exists as a directory.")
        return INVALID_PARAMETER
    else:
        with open(path, "ab" if append else "wb") as file:
            if(append):
                file.seek(0, 2)
            file.write(data)
        update_client(idx, "Finished writing data to {}".format(path))
        return SUCCESS


@register_command
def touch(idx, path):
    '''
    Similar in function to Linux's touch. If the user passes in a path that
    points to a directory, then will notify the client and return
    INVALID_PARAMETER/. Otherwise, firstly it checks to see if the path points
    to a file or not. If it doesn't point to a file, this function will create
    an empty file. If the file exists, then this function will update the
    modification time on the file without changing its content. In both cases,
    will report to the client of completion and return SUCCESS.

    :param path: Path to file to touch.
    :type path: str

    :returns: SUCCESS if able to touch file. INVALID_PARAMETER if path exists as
        a directory.
    '''
    if(os.path.exists(path) and os.path.isdir(path)):
        update_client(idx, "wrfile: Path exists as a directory.")
        return INVALID_PARAMETER
    else:
        file = open(path, "ab+" if os.path.exists(path) else "wb+")
        file.write(b" ")
        file.flush()
        file.seek(-1, 2)
        file.truncate()
        file.close()
        update_client(idx, "Touched {}".format(path))
        return SUCCESS


@register_command
def jobs(idx):
    '''
    Checks to see all the JOBS that are still running in the server as
    background taks and notifies the client of them.

    :returns: SUCCESS
    '''
    output = ""
    for key, value in JOBS.items():
        if(value is not None):
            output += "Running {}: {}\n".format(key, value[2:])
    if(output == ""):
        output = "No jobs running."
    update_client(idx, output)
    return SUCCESS


@register_background_command
def exec(idx, queue, cmd):
    '''
    Runs as a background command. This function is used to run commands on the
    system by executing commands directly. Exec begins by creating a new
    :class:`console.ConsoleExecutor` and begins listening to any output. Every
    10 ms or every time it receives an output, exec will check to see if there
    are any traffic on the queue linked to the main server. Currently, the
    server may pass in any input to send to the subprocess running the external
    command or for the command to kill the subprocess.

    For any output read by exec, it will notify the client. Finally, when the
    subprocess exits, will notify the client for the completion.

    :param cmd: Command in string to run on the system. These are unique to each
        OS so users should know beforehand what the usecase is.
    :type cmd: str

    :returns: SUCCESS
    '''
    m_executor = ConsoleExecutor(cmd)
    while(m_executor.alive or not(m_executor.empty)):
        try:
            line = m_executor.read_output(0.01)
            if(line is not None):
                update_client(idx, line)
        except ConsoleExecTimeout:
            pass
        if(not(queue.empty())):
            command = queue.get()
            if(command["type"] == INPUT):
                m_executor.send_input(command["value"])
            elif(command["type"] == KILL):
                m_executor.close()
                break
    m_executor.close()
    return m_executor.returncode


@register_command
def send_input(idx, job_num, value):
    '''
    For the jobs that follow the default queue pattern, this method sends a
    INPUT command to the background job with the associated value. The
    background threads will then read this command and send them to the
    corresponding process. I.e. for exec, since exec is listening for output
    from the subprocess, exec bg thread is also listening for any traffic in
    the queue. If the job doesn't exist or has already completed, will notify
    the user of such and return INVALID_PARAMETER. Otherwise, push the request
    into the queue and return success.

    :param job_num: ID of the job to pass this message to.
    :type job_num: int
    :param value: Send input as string to the job.
    :type value: str

    :returns: SUCCESS if able to send input to job. INVALID_PARAMETER if job
        doesn't exist or has already exited.
    '''
    if(job_num in JOBS and JOBS[job_num] is not None):
        JOBS[job_num][QUEUE_IDX].put({"type": INPUT, "value": value})
        update_client(idx, "Sent value to job {}".format(job_num))
        return SUCCESS
    else:
        update_client(idx, "Job does not exist or has already completed...")
        return INVALID_PARAMETER


@register_command
def is_alive(idx, job_num):
    '''
    Checks to see if the job is still alive or has exited. Informs the client
    True if the job is still alive. False otherwise. Always returns SUCCESS.

    :param job_num: ID of the job to check.
    :type job_num: int

    :returns: SUCCESS
    '''
    if(job_num in JOBS and JOBS[job_num] is not None):
        update_client(idx, True)
    else:
        update_client(idx, False)
    return SUCCESS


@register_command
def kill(idx, job_num):
    '''
    For the jobs that follow the default queue pattern, this method sends a
    KILL command to the background job with the associated value. The
    background threads will then read this command and terminate the
    corresponding process. I.e. for exec, since exec is listening for output
    from the subprocess, exec bg thread is also listening for any traffic in
    the queue.

    :param job_num: ID of the job to pass this message to.
    :type job_num: int

    :returns: SUCCESS if able to send kill command to job. INVALID_PARAMETER if
        job doesn't exist or has already exited.
    '''
    if(job_num in JOBS and JOBS[job_num] is not None):
        JOBS[job_num][QUEUE_IDX].put({"type": KILL})
        update_client(idx, "Sent kill command to job {}".format(job_num))
    else:
        update_client(idx, "Job does not exist or has already completed...")
        return INVALID_PARAMETER


@register_command
def close_server(idx):
    '''
    Kills any jobs that are running in the background and awaits for them to
    respond. Updates the client with all of the jobs that have been killed.

    Finally, updates the client of the incoming closure and returns SUCCESS. The
    main loop of the server will recognize that close_server has been called and
    exit.

    :returns: SUCCESS
    '''
    for key, job_tuple in JOBS.items():
        if(job_tuple is not None):
            job_tuple[QUEUE_IDX].put({"type": KILL})
            update_client(idx, "Killing job {}".format(key))
            job_tuple[THREAD_IDX].join()

    update_client(idx, "Closing Server")
    return SUCCESS


@register_command
def os_info(idx):
    '''
    Can be used to determine the type of OS running on the server. Updates the
    client with "windows", "linux", or "mac".

    :returns: SUCCESS
    '''
    update_client(idx, os_name())
    return SUCCESS


@register_command
def user_name(idx):
    '''
    Used to determine the name of user who's logged in, mainly for local directory
    naming.

    :returns: SUCCESS
    '''
    update_client(idx, os.getlogin())
    return SUCCESS


@register_command
def reboot(idx):
    '''
    Issues a reboot command to the server based on which OS this server is
    running on. For all of the cases, we simply notify the user of the
    inevitable shutdown of the system.

    :returns: SUCCESS

    .. note:: This job may not respond with COMPLETE, depending on how fast the
        OS reboots the system...
    '''
    my_os = os_name()
    update_client(idx, "Requesting os to reboot")
    if(my_os == "windows"):
        os.system("shutdown -t 0 -r -f")
    elif(my_os == "linux"):
        os.system("/sbin/reboot now")
    elif(my_os == "mac"):
        raise NotImplementedError("Macs not supported at the moment")
    return SUCCESS


@register_command
def shutdown(idx):
    '''
    Issues a shutdown command to the server based on which OS this server is
    running on. For all of the cases, we simply notify the user of the
    inevitable shutdown of the system.

    :returns: SUCCESS

    .. note:: This job may not respond with COMPLETE, depending on how fast the
        OS shutdowns the system...
    '''
    my_os = os_name()
    update_client(idx, "Requesting os to shutdown")
    if(my_os == "windows"):
        os.system("shutdown -t 0 -s -f")
    elif(my_os == "linux"):
        os.system("/sbin/shutdown now")
    elif(my_os == "mac"):
        raise NotImplementedError("Macs not supported at the moment")
    return SUCCESS


@register_command
def sleep(idx):
    '''
    Puts the system into S3 state.
    '''
    my_os = os_name()
    update_client(idx, "Requesting os to sleep")
    if(my_os == "windows"):
        os.system("{}\\System32\\rundll32.exe powrprof.dll,SetSuspendState 0,1,0".format(os.environ['windir']))
    elif(my_os == "linux"):
        raise NotImplementedError("Sleep not supported at moment for linux")
    elif(my_os == "mac"):
        raise NotImplementedError("Macs not supported at the moment")
    return SUCCESS
