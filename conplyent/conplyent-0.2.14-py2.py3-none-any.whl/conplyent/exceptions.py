'''
:File: exceptions.py
:Author: Jayesh Joshi
:Email: jayeshjo1@utexas.edu
'''

import sys
import traceback


class ZMQPairTimeout(RuntimeError):
    '''
    Lower level timeout raised by ZMQPair when sending or receiving messages.
    Client/Server implementation should intercept this so users shouldn't need
    to worry about it.
    '''
    pass


class ConsoleExecTimeout(RuntimeError):
    '''
    Timeout raised by ConsoleExecutor if the executor did not respond in the
    amount of time specified by user.
    '''
    pass


class ClientTimeout(RuntimeError):
    '''
    Timeout raised by Client when the server did not repsond in the amount of
    time specified by user.
    '''
    pass


def exception_to_str():
    '''
    When python throws an error, users can catch the error and call this
    function to retrieve the entire call trace and the exception message in
    string format.

    :returns: String format detailing call stack and exception message.
    '''
    exc_type, exc_value, exc_traceback = sys.exc_info()
    return ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))


def min_exception_to_str():
    '''
    When python throws an error, users can catch the error and call this
    function to retrive only the exception message in string format.

    :returns: String format detailing the exception message.
    '''
    exc_type, exc_value, exc_traceback = sys.exc_info()
    return exc_value
