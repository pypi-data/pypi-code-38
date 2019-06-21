'''
:File: client.py
:Author: Jayesh Joshi
:Email: jayeshjo1@utexas.edu
'''

import time
import inspect
import os
from threading import local

from ._zmq_pair import ZMQPair
from ._msg import MSG, MSGType
from .exceptions import ZMQPairTimeout, ClientTimeout
from ._decorators import timeout
from ._general import logger
from .server import INVALID_PARAMETER, ERROR

_pool = local()


def add(hostname, port=9922):
    '''
    Clients can be added using this method which registers the a connection to a
    local pool to allow for creation of many clients. This creates a class
    :class:`client.ClientConnection` which will allow users to communicate
    with the server existing on a different process (local or remote).

    This does not establish the connection.

    :param hostname: Host name of the server.
    :type hostname: str
    :param port: Port number that the server is listening to.
    :type port: int
    '''
    connection = ClientConnection(_new_connection(ZMQPair(dest_ip=hostname, port=port)))
    return connection


class ClientConnection():
    '''
    Client connection class that provides the means to connect to a local or
    remote server and execute commands. These commands are defined in the
    server module. This class will request to sync methods with the
    remote server which will provide all available methods. Users using the
    ClientConnection class can easily send commands over to the remote server as
    if just calling class methods.

    :Example:

    >>> from conplyent import client
    >>> my_conn = client.add_client("localhost")
    >>> my_conn.connect()
    >>> my_conn.ls()

    These methods are not initially defined in the client class so the
    Connection will not be able to provide the methods intiially. Attempting to
    run commands at this point will result in AttributeError.

    Once the connection has been established, users can use
    :meth:`client.ClientConnection.server_methods` to view all of the commands.
    This method does not provide any keyword parameters though. May look into
    doing so in the future. When using these commands, users can access the
    server methods using any args or kwargs combination as defined in the server
    methods. These methods will have the same requirements as defined in the
    server. I.e. order sent to server is the order defined in the server
    methods. And the kwargs follow the same name:value format as the server.

    Both of these are valid:

    >>> my_conn.cd("..")
    >>> my_conn.cd(dest="..")

    Any errors resulted by user input will be passed back to the client. These
    will not crash the server. For example, if we pass in an int to 'cd'
    command, this command will output the complete traceback provided by the
    server.

    :cd(1):

    >>> TypeError('chdir: path should be string, bytes or os.PathLike, not int')

    When using these server methods, users can provide three additional kwargs
    to the method that are processed client side. These are "timeout",
    "complete", "echo_response", "max_interval", and "raise_error".

    Timeout defines the amount of time that we want to wait for the send command
    to go through. This could come into play for scenarios where you have a
    bunch of network activity on the host so that send command may take a while
    to go through ZMQ. By default timeout is None, so the send will be
    guaranteed to go through (though no promises on how long it may take). On a
    typical system where you have a more relaxed network activity, this send
    should go through immedaitely.

    Complete can be disabled to have more control over how the this class
    receives outputs from the server. If complete is set to True (as is
    default), once the command has been sent, this class will continually
    attempt to receives the output from the server and append to a list that is
    returned. If complete is set to False, these methods will return a
    :class:`client.ClientConnection.ClientListener` instance which the user can
    use themselves to listen to the output in real time. This is mostly useful
    when we are running background tasks. These tasks will still continue to be
    executed in the server but we don't need to wait for it. Examples of use
    cases: If we need to send input to the task, if we want to kill it
    prematurely, or if we want to parse and process the output in real time.
    See description of jobs for more information.

    :complete=False:

    >>> listener = my_conn.exec("some_long_command", complete=False)
    >>> ... do something else ...
    >>> for response in iter(listener.next, None):
    >>>     ... do something with response ...

    Echo Response will simply print to stdout the response in real time. This
    can be useful when users have enabled complete.

    Max Interval determines the amount of time that the listener should wait
    between each message. This should be used when you expect that the program
    being run on the system under test should respond every x interval and not
    doing so is a significance of the server crashing, whether due to
    application error or due to server in an unstable state. If the server does
    not respond between each messages larger than user set max_interval, then
    listener will throw a ClientTimeout error. Max Interval is defined in
    seconds, and can be sent as a floating number to specify lower granularity.
    For cases where complete is set to False, max_interval can later be adjusted
    through the property exposed by ClientListener.

    :max_interval=#:

    >>> my_conn.exec("check_system_stability", max_interval=10, complete=True)

    Raise Error is by default set to False. Command sent to the server can
    return either INVALID_PARAMETER, which is a field returned by server
    commands noting that the parameter sent by user is invalid, or ERROR, noting
    that the command failed due to some exception. If Raise Error is set to
    True, then INVALID_PARAMETER responses will raise a ValueError, and ERROR
    responses will raise the error retrieved.
    '''

    def __init__(self, conn_id, enter_connect=True, enter_connect_timeout=None):
        self.__conn_id = conn_id
        self.__synced = False
        self.__initial_methods = [i[0] for i in [k for k in inspect.getmembers(self, inspect.ismethod)]]
        self.__enter_connect = enter_connect
        self.__enter_connect_timeout = enter_connect_timeout

    def __enter__(self):
        if(self.__enter_connect):
            self.connect(timeout=self.__enter_connect_timeout)
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def connect(self, timeout=None):
        '''
        Finds the ZMQPair from the local pool and try to establish connection.
        Once the connection is established, will wait until we get a response
        from the server guaranteeing that the server is alive. ZMQ connection
        success just means that we have been able to own the port of the
        localhost to be able to send commands, does not guarantee that we have
        made a handshake with the server.

        Users may pass in timeout for how long we should wait to see if the
        server responds. This can be useful in the cases where we have pulsed a
        reboot or shutdown request to the server so this connect method will
        wait for the server to come back alive.

        :Optional:

        :param timeout: Amount of time in seconds to wait for the connection to
            be established. None = wait forever (nonblocking).
        :type timeout: (int)

        :raises ConnectionError: If server does not respond in the desired
            amount of time.
        '''
        connection = _get_connection(self.__conn_id)
        connection.connect()
        if(timeout):
            logger.info("Waiting {}s for {} to respond...".format(timeout, self.__conn_id))
        else:
            logger.info("Waiting for {} to respond...".format(self.__conn_id))
        if(not(connection.pulse(timeout))):
            raise ConnectionError("Server not responding at {}".format(self.__conn_id))
        if(not(self.__synced)):
            self.__sync_attr()
            self.__synced = True
            logger.info("Synced with server.")

    def close(self):
        '''
        Completely closes the socket used to communicate to the server. This
        should only be called when the client is finished communicating with the
        server. For temporary disconnects, use
        :meth:`client.ClientConnection.disconnect`.

        This will prevent this connection class from working in the future. User
        will need to add a new connection to communicate with the server.
        '''
        connection = _get_connection(self.__conn_id)
        connection.close()
        logger.info("Closing connection to {}".format(self.__conn_id))
        time.sleep(0.001)

    def disconnect(self):
        '''
        Disconnects with the server. Commands can no longer be sent.

        This is useful for cases when the server drops connection and we need to
        re-establish connection by disconnecting the socket prematurely.
        '''
        connection = _get_connection(self.__conn_id)
        connection.disconnect()
        logger.info("Disconnecting {}".format(self.__conn_id))
        time.sleep(0.001)

    def server_methods(self):
        '''
        When user calls connect, this connection class will sync with the server
        to gather all of the possible commands that can be sent to the server.
        These commands are added as new attributes for this class.

        .. note:: This should only be called once the connection has been
            established. Otherwise will return nothing.
        '''
        commands = [i[0] for i in [k for k in inspect.getmembers(self, inspect.ismethod)]]
        return list(filter(lambda k: not (k[0] == "_" or k in self.__initial_methods), commands)) + ["transfer"]

    def heartbeat(self, timeout=None):
        '''
        Checks to see if the server is still alive by sending a simple Heartbeat
        request. Even if server is executing tasks in the background, the main
        server is mainly just waiting for client requests. This means that This
        request should be honored immediately. By default, this method will wait
        forever for a response from the server. Users may pass in a timeout to
        see if the server will respond in that amount of time.

        :Optional:

        :param timeout: Time in seconds to wait for a heartbeat response
        :type timeout: int

        :returns: True if the server responded. False if timed out.
        '''
        connection = _get_connection(self.__conn_id)
        return connection.pulse(timeout=timeout)

    def transfer(self, src, dest, chunk=1024, timeout=None, **kwargs):
        '''
        Transfers file from client to server.

        :param src: Path to file on client
        :type src: str
        :param dest: Destination to save on server
        :type dest: str

        :Optional:

        :param chunk: Amount in bytes to send per transaction. (1024)
        :type chunk: int
        :param timeout: Time to wait for commands to be sent.
        :type timeout:
        '''
        self.mkdirs(os.path.dirname(dest), exist_ok=True, timeout=timeout, **kwargs)
        append = False
        with open(src, "rb") as file:
            while(True):
                data = file.read(chunk)
                if(data == b''):
                    break
                else:
                    self.wrfile(dest, data, append=append, timeout=timeout, **kwargs)
                    append = True

    def _command_server(self, cmd_id, *args, timeout=None, complete=True, echo_response=False, max_interval=None,
                        raise_error=False, **kwargs):
        listener = self.__send_command(cmd_id, timeout=timeout, max_interval=max_interval, *args, **kwargs)
        if(complete):
            output = list()
            for response in iter(listener.next, None):
                output.append(response)
                if(echo_response):
                    print(response.rstrip() if type(response) is str else response)
            if(raise_error):
                if(listener.exit_code == ERROR):
                    raise output[-1]
                elif(listener.exit_code == INVALID_PARAMETER):
                    raise ValueError(output[-1])
            return output[1:]  # ignore the echo of command
        else:
            return listener

    def __send_command(self, cmd_id, *args, timeout=None, max_interval=None, **kwargs):
        connection = _get_connection(self.__conn_id)
        msg = MSG(MSGType.COMMAND, cmd_id=cmd_id, args=args, keywargs=kwargs)
        connection.send_msg(msg, timeout)
        logger.debug("Sent Message: {}".format(msg))
        return ClientConnection.ConnectionListener(connection, max_interval)

    def __sync_attr(self, timeout=None):
        connection = _get_connection(self.__conn_id)
        connection.send_msg(MSG(MSGType.SYNC, request=True))
        extra_list = list()
        while(True):
            msg = connection.recv_msg(timeout=timeout)
            if(msg.type == MSGType.SYNC):
                for name in msg.args[0]:
                    setattr(ClientConnection, name, _wrap_server_methods(self, name))
                break
            else:
                extra_list.append(msg)
        for extra in extra_list:
            connection.requeue_msg(extra)

    class ConnectionListener():
        '''
        This class is created when users send command over to the server. This
        class is instantiated by :class:`client.ClientConnection` and should not
        be initialized by the user.

        Used to read in message updates by the job and keep track of attributes
        related to the job such as described below. Initially, this class will
        wait for a handshake response by the server acknowledging that the
        server has begun the request. This could wait forver if the server fails
        to acknowlege the request, whether if the server's network is full or if
        the server has crashed. The later is highly unlikely to be the case,
        since this listener object will only be created after the server has
        been checked for a heartbeat.
        '''

        def __init__(self, connection, max_interval):
            self.__connection = connection
            self._done = False
            self._exit_code = None
            self._max_interval = max_interval
            self.__find_ack()
            self.__curr_msg = 0

        def __enter__(self):
            return self

        def __exit__(self, type, value, traceback):
            pass

        @property
        def done(self):
            '''
            Used to determine whether a job is complete or not. This is only set
            when Listener has finished reading all of the messages. If the job
            has completed on the server side, but the user has not gone through
            all of the messages using
            :meth:`client.ClientConnection.ClientListener.next`, then this will
            still read as False.

            :getter: (bool) True if job has been completed. False otherwise.
            '''
            return self._done

        @property
        def exit_code(self):
            '''
            Server methods exit with a return code. Default conplyent server
            methods follow 0 = success, 1 = error in runtime, -1 = bad
            parameter.

            :getter: (int) Exit code of server method. None if job has not
                completed.
            '''
            return self._exit_code

        @property
        def id(self):
            '''
            Unique ID given to each job. This ID is required for some of the
            server methods which interacts with backkground jobs, such as
            sending input or killing the said job.

            :getter: (int) Unique ID assigned to job.
            '''
            return self._id

        @property
        def max_interval(self):
            '''
            Max interval between two messages that this listener will receive.
            If this value is None, there will be no timeout. If this value is
            a positive integer, then Listener will timeout if messages are not
            retrieved within the max_interal.

            :getter: Get the max interval setting of this listener
            :setter: Sets the max interval setting of this listener. Setting
                must be either None, or positive integer
            '''
            return self._max_interval

        @max_interval.setter
        def max_interval(self, value):
            assert value is None or type(value) is int and value >= 0, "Timeout must be None or positive integer"
            self._max_interval = value

        def next(self):
            '''
            Checks to see if there has been any messages for this job. By
            default, will keep waiting until a message has arrived. Users can
            override this passing in timeout to wait only a set amount of time
            for each message to the initialization of this listener.

            :returns: Update provided by the job, or None if: (Job has
                Completed, timed out waiting for message, or connection with
                server has been interrupted)

            :raises ClientTimeout: If user specifies timeout and message is not
                received in the given time.

            .. warning:: If the job has already completed, this method should
                not be called and will throw an AssertionError.
            '''
            self.__response = None
            assert not(self._done), "Server has already completed job..."
            try:
                self.__receive_message(timeout=self._max_interval, exception=ClientTimeout)
            except (ZMQPairTimeout):
                raise ClientTimeout("Server did not respond in {} s".format(timeout))
            return self.__response

        def clear_messages(self):
            '''
            Goes through all of the messages sent by the server in regards to
            this command and clears them out. This will NOT return anything.
            Does not raise ClientTimeout error. Users should check with done
            property to determine whether the command is complete or not.

            Useful if you don't care about the output and want to continue until
            timeout.
            '''
            try:
                for msg in iter(self.next, None):
                    pass
            except ClientTimeout:
                return

        @timeout(name="Listening")
        def __receive_message(self, *args, **kwargs):
            while(True):
                msg = self.__connection.recv_msg(timeout=kwargs["timeout"], msg_id=self.id)
                if((msg.type == MSGType.COMPLETE or msg.type == MSGType.DETAILS) and
                   msg.request_id == self._id and msg.msg_num == self.__curr_msg):
                    self.__curr_msg += 1
                    if(msg.type == MSGType.COMPLETE):
                        self._done = True
                        self.__response = None
                        self._exit_code = msg.exit_code
                    else:
                        self.__response = msg.details
                    break
                else:
                    self.__connection.requeue_msg(msg)
                    yield None  # This will let other threads try to get the message

        def __find_ack(self, timeout=None):
            while(True):
                try:
                    msg = self.__connection.recv_msg(timeout=self._max_interval)
                    if(msg.type == MSGType.ACKNOWLEDGE):  # There should always be only a single ack coming back
                        self._id = msg.request_id
                        break
                    else:
                        self.__connection.requeue_msg(msg)
                        time.sleep(0)  # some other thread probably wanted that message...
                except ZMQPairTimeout:
                    raise ClientTimeout("Slave did not acknowledge request in {}s".format(timeout))


def _new_connection(conn):
    # Checks to see if connection with the same ID exists. If so, will close it and set the new ID. Otherwise just set
    # new ID
    conn_id = "{}:{}".format(conn.dest_ip, conn.port)
    try:
        connection = _get_connection(conn_id)
        connection.close()
    except RuntimeError:
        pass
    _pool.__dict__.setdefault("conplyent_pool", dict())[conn_id] = conn
    return conn_id


def _get_connection(conn_id):
    # Gets the connection from local pool.
    try:
        return getattr(_pool, "conplyent_pool")[conn_id]
    except (AttributeError, KeyError, IndexError):
        raise RuntimeError("Connection {} has not been set up".format(conn_id))


def _wrap_server_methods(cls, name):
    # Used to set new commands as attributes to the client connection
    def wrapper(self, *args, **kwargs):
        return self._command_server(name, *args, **kwargs)
    return wrapper
