#!/usr/bin/env python3

import pickle
import os
from zlib import crc32
from collections import OrderedDict

"""
Functionfaker provides a decorator to store and retrieve ("replay") function responses to inputs (arguments). A key is generated from the function inputs, and the function output is stored against that key. The next time the function is called with the same input, the same key is generated from this input, and the previously saved response is retrieved.

This code provides a basic storage mechanism in the Store class, using a simple Pickle file to store the responses, and crc32 to generate the keys. To implement your own storage and/ or key generation, create a Store class that implements an update and get_response method, and hash_args method to implement your own key generation.
"""

# ------ Storage classes ------------
# Replace the following classes with your own to implement different storage and hashing methods.

class BaseStore(object):
    """ Base class providing hashing method. Make your own by overriding the hash_args method.
    """

    def hash_args(self, function_args ):
        """ Create key from function arguments

        Args
            function_args (list): function arguments
        """

#        print(function_args)

        return crc32(pickle.dumps(sort_object(function_args)))


class Store(BaseStore):
    """Response class. Must provide update and get_response
    """

    def __init__(self, fname = "responses.p"):
#        super(, self).__init__()
        self.fname = fname


    def _load_responses(self ):

        responses = {}
        if os.path.exists(self.fname ):
            with open(self.fname, "rb") as f:
                responses = pickle.load(f)

        return responses

    def _save_responses(self, responses):

        with open(self.fname, "wb") as f:
            pickle.dump(responses, f)

    def update(self, store_key, function_return):

        responses = self._load_responses()
        responses[store_key] = function_return
        self._save_responses(responses)

    def get_response(self, store_key, default_return = None):

        responses = self._load_responses()
        if store_key in responses:
            return responses[store_key], True
        else:
            return default_return, False

    def clear(self):
        if os.path.exists(self.fname):
            os.remove(self.fname)

# default storage to use.
store = Store()

# ---- function faker procedural code --------

def ignore_args(function_args, args2ignore, ignore_value = None):
    """ Remove argument values to be ignored.

    Args:
        function_args: list of function arguments.
        args2ignore: list of integers representing index in argument list.
        ignore_value: value to substitute in ignored arguments.
    """

    function_args = list(function_args)
    for i in args2ignore:
        function_args[i] = ignore_value

    return function_args

# Functions related to the main decorator.

def sort_object(obj):
    """ Sort nested dictionary objects to obtain more predictable behavior on storage.
    """

    if isinstance(obj, dict):
        new_D = []
        for k, v in sorted(list(obj.items())):
            new_D.append( (k, sort_object(v)) )

        return OrderedDict(new_D)

    elif isinstance(obj, (list, tuple)):
        return [sort_object(e) for e in obj]
#    elif hasattr(obj, '__dict__'):
#        obj.__dict__ = sort_object(obj.__dict__)
#        return obj

    return obj

def record_responses_for_decorator(function_return, function_args, store = store):
    """ Create and store mock function responses from real responses and store them by function argument tuples.

        To be called from inside decorator
    """

    print('Recording response function "%s"'%function_args[0])

    store_key = store.hash_args(function_args)
    store.update(store_key, function_return)

    return function_return


def make_fake_fun(default_return = None, store = store):
    """ Make function that fakes (memoizes) real function.

    Args
        args2ignore: (list of strings) list of function arguments to ignore
        default_return: function return value if function response is not found

    Returns
        Function that returns recorded responses.
    """
    def fake_fun(*args, **kwargs):
        """ Function that loads and returns responses by keys
        """

        store_key = store.hash_args(args)
        return_value, success = store.get_response(store_key)
        status = 'found' if success else 'not found'
        print('Faking function "%s". Response %s'%(args[0], status))

        return return_value

    return fake_fun



# The main decorator
def response_player(args2ignore = [], default_return = None, store = store):
    """ Function recorder/ player decorator for function to be faked.

    Records or replays depending on RECORD environment variable.
    RECORD environment variable can be set to replay or record. If set to replay, the decorator will cause the real function call to be replaced by a pre-recorded response (the "fake" function). If set to record, the real function will be called, and its return value stored ("recorded").
    If not set to either, this decorator function will proceed without any additional action.

    The decorator uses a store object to manage storage and retrieval of function responses, with a default object provided. To implement your own storage and/ or key generation, create a Store class that implements an update and get_response method, and hash_args method to implement your own key generation.

    Args
        args2ignore: (list of strings) list of function arguments to ignore
        default_return: function return value if function response is not found
        store: Store object to manage storage and retrieval of function responses (default object provided)

    Returns
        Decorator to use on any function or method to be recorded

    """
    def response_decorator(func):
        def func_wrapper(*args, **kwargs):
            args = ignore_args(args, args2ignore)

            # key to recorded function responses contains function name
            args_plus_fun = tuple([func.__name__, ] + list(args) + [kwargs, ] )
            if os.environ.get("RECORD","live") == "replay":
                fake_fun = make_fake_fun(default_return = default_return, store = store)
                return fake_fun(*args_plus_fun, **kwargs)
            else:
                # catch response from real function func
                result = func(*args, **kwargs)
                if os.environ.get("RECORD","live") == "record":
                    record_responses_for_decorator(function_return = result, function_args = args_plus_fun, store = store)
                return result
        return func_wrapper
    return response_decorator



if __name__ == "__main__":

    pass
