'''
:File: console.py
:Author: Jayesh Joshi
:Email: jayeshjo1@utexas.edu
'''

import psutil
from subprocess import Popen, PIPE, STDOUT
from threading import Thread
from queue import Queue

from ._decorators import timeout
from .exceptions import ConsoleExecTimeout


class ConsoleExecutor():
    '''
    Simple wrapper around subprocess to provide a non-blocking read from
    stdout and stderr. This executor will start the subprocess using
    universal_newlines=True, shell=False, and start_new_session=True to provide
    the most responsive and proper executor. If the user specifies any kwargs
    that should be sent to Popen, then they can override these settings.

    This subprocess will start as the class is initialized and the class will
    start a background thread that continually reads the output from the
    executor. This way, if the user wants to read the output, we can simply
    check to see if the background thread has done anything by timing out this
    main thread and allowing the background thread to do its job. This also
    allows users to timeout any read requests if user just wants to check if
    there are any output.

    This class also provides other interactive means to communicate with the
    subprocess such as sending input and terminating.
    '''

    def __init__(self, cmd, **kwargs):
        self._cmd = cmd
        if(kwargs):
            self.__popen = Popen(cmd, stdout=PIPE, stderr=STDOUT, stdin=PIPE, **kwargs)
        else:
            self.__popen = Popen(cmd, stdout=PIPE, stderr=STDOUT, stdin=PIPE, universal_newlines=True, shell=False,
                                 start_new_session=True)
        self.__queue = Queue()
        self.__bg_worker = Thread(target=ConsoleExecutor.__file_reader, args=(self.__queue, self.__popen.stdout))
        self.__bg_worker.start()
        self._alive = True

    @property
    def cmd(self):
        '''
        Command linked to this executor.

        :getter: (int command that is being executed.
        '''
        return self._cmd

    @property
    def returncode(self):
        '''
        Exit code from the subprocess. Only set once the subprocess has exited.

        :getter: (int) any exit code from process
        '''
        return self.__popen.returncode

    @property
    def alive(self):
        '''
        Determines if the subprocess is still alive or not. The background
        thread used to read in any output from the subprocess will have exited
        once the subprocess has completed.

        :getter: (bool) True if subprocess is still alive. False if completed or
            exited otherways.
        '''
        return self.__bg_worker.is_alive()

    @property
    def empty(self):
        '''
        Determines if there is no more output left in the bg executor.

        :getter: (bool) True if no more output. False otherwise
        '''
        return self.__queue.empty()

    def read_output(self, timeout=None):
        '''
        Reads the next output from the subprocess. These must be sent by flushed
        stdout or stderr.

        By default, this method will poll forever until the subprocess has
        passed any output. Users can define timeout to wait only a specific
        amount of time for the next output.

        :param timeout: Amount of time in seconds to wait for the next output.
        :type timeout: int

        :returns: Output read from the subprocess. This value will be None if
            the subprocess has exited.

        :raises ConsoleExecTimeout: If user specifies a non-None/non-Negative
            timeout and subprocess has not responded in time.
        '''
        if(not(self.__queue.empty())):
            return self.__queue.get()
        while(True):
            if(self.alive):
                self.__poll_queue(timeout=timeout, exception=ConsoleExecTimeout)
                if(self.__queue.empty()):
                    if(not(self.alive)):
                        self.__popen.wait()
                        if(not(self.__queue.empty())):
                            return self.__queue.get()
                    return None
                else:
                    return self.__queue.get()  # should never halt here...
            else:
                self.__popen.wait()
                if(not(self.__queue.empty())):
                    return self.__queue.get()
                return None

    def send_input(self, value, new_line=True):
        '''
        Allows users to send input to the subprocess. This input will be flushed
        into the subprocess to ensure that the input will be read. To acheive
        this, this method will automatically add an extra new line if the user
        hasn't specified a new line. This automatic behavior can be disabled by
        optional user input new_line

        :param value: Message to send to the subprocess.
        :type value: str
        :param new_line: True if method should add a new line if missing. False
            to ignore this feature.
        :type new_line: bool
        '''
        if(self.alive):
            self.__popen.stdin.write(value + "\n" if value[:-1] != "\n" and new_line else value)
            self.__popen.stdin.flush()

    def kill(self):
        '''
        Terminates the subprocess and waits for it to exit gracefully. Currently
        this will not stop any child processes spawned by our subprocess.
        '''
        self.__kill_proc_tree()
        self.__popen.terminate()
        self.__popen.wait()

    def close(self):
        '''
        Closes off any FDs open by this class to properly clear any memory used
        by this subprocess. Terminates subprocess if alive.
        '''
        if(self.alive):
            self.kill()
        self.__bg_worker.join()
        self.__popen.wait()
        self.__popen.stdin.close()
        self.__popen.stdout.close()

    @timeout(name="Polling Subprocess")
    def __poll_queue(self, **kwargs):
        while(self.__queue.empty() and self.__bg_worker.is_alive()):
            yield None

    def __file_reader(queue, file):
        for line in iter(file.readline, b'' or ''):
            queue.put(line)
        file.close()

    def __kill_proc_tree(self):
        '''
        Borrow:
        https://stackoverflow.com/questions/1230669/subprocess-deleting-child-processes-in-windows
        '''
        parent = psutil.Process(self.__popen.pid)
        children = parent.children(recursive=True)
        for child in children:
            child.kill()
        gone, still_alive = psutil.wait_procs(children, timeout=5)
