#!/usr/bin/env python3

import pickle
import os
from zlib import crc32
from collections import OrderedDict


def load_responses(fname):

    responses = {}
    if os.path.exists(fname ):
        with open(fname, "rb") as f:
            responses = pickle.load(f)

    return responses

def save_responses(responses, fname = "responses.p"):

    with open(fname, "wb") as f:
        pickle.dump(responses, f)

def update_responses(store_key, function_return, fname = "responses.p"):

    responses = load_responses(fname)
    responses[store_key] = function_return
    save_responses(responses, fname)

def get_response(store_key, fname = "responses.p", default_return = None):

    responses = load_responses(fname)
    if store_key in responses:
        return responses[store_key], True
    else:
        return default_return, False

def sort_object(obj):

    if isinstance(obj, dict):
        new_D = []
        for k, v in sorted(list(obj.items())):
            new_D.append( (k, sort_object(v)) )

        return OrderedDict(new_D)

    elif isinstance(obj, (list, tuple)):
        return [sort_object(e) for e in obj]
    elif hasattr(obj, '__dict__'):
        obj.__dict__ = sort_object(obj.__dict__)
        return obj

    return obj


def hash_args(function_args, args2None=[] ):
    """ Create key from function arguments

    Args
        function_args (list): function arguments
        args2None (list of ints): list indexes of functions args to ignore
    """

    function_args = list(function_args)
    for i in args2None:
        function_args[i] = None

    return crc32(sort_object(pickle.dumps(function_args)))


def record_responses_for_decorator(function_return, function_args, args2None = []):
    """ Create and store mock function responses from real responses and store them by function argument tuples.

        To be called from inside decorator
    """

    print('Recording response function "%s"'%function_args[0])

    store_key = hash_args(function_args, args2None)
    update_responses(store_key, function_return)

    return function_return


def make_fake_fun(args2None, default_return = None):
    """ Make function that spoofs real function.

    Args
        args2None: (list of strings) list of function arguments to ignore
        default_return: function return value if function response is not found

    Returns
        Function that returns recorded responses.
    """
    def fake_fun(*args, **kwargs):
        """ Function that loads and returns responses by keys
        """

        store_key = hash_args(args, args2None)
        return_value, success = get_response(store_key)
        status = 'found' if success else 'not found'
        print('Faking function "%s". Response %s'%(args[0], status))

        return return_value

    return fake_fun



# Decorator
def response_player(args2None = [], default_return = None):
    """ Function recorder/ player decorator for function to be faked.

    Records or replays depending on RECORD environment variable.
    RECORD environment variable can be set to replay or record. If set to replay, the decorator will cause the real function call to be replaced by a pre-recorded response (the "fake" function). If set to record, the real function will be called, and its return value stored ("recorded").
    If not set to either, this decorator function will proceed without any additional action.

    Args
        args2None: (list of strings) list of function arguments to ignore
        default_return: function return value if function response is not found

    Returns
        Decorator

    """
    def response_decorator(func):
        def func_wrapper(*args, **kwargs):
            # key to recorded function responses contains function name
            args_plus_fun = tuple([func.__name__, ] + list(args) + [kwargs, ] )
            if os.environ.get("RECORD","live") == "replay":
                fake_fun = make_fake_fun(args2None = args2None, default_return = default_return)
                return fake_fun(*args_plus_fun, **kwargs)
            else:
                # catch response from real function func
                result = func(*args, **kwargs)
                if os.environ.get("RECORD","live") == "record":
                    record_responses_for_decorator(function_return = result, function_args = args_plus_fun, args2None = args2None)
                return result
        return func_wrapper
    return response_decorator



if __name__ == "__main__":

    pass
