"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import jwt
import base64
import hashlib
import logging
from datetime import datetime

from collections import namedtuple

from .exceptions import BadTokenException


def md5sum(file_name, blocksize=65536):
    """
    Computes md5sum on a fileself.

    :param file_name: The name of the file on which to compute the md5sum.
    :return: Hexdigest of md5sum for file.
    """
    md5 = hashlib.md5()
    with open(file_name, "rb") as f:
        for block in iter(lambda: f.read(blocksize), b""):
            md5.update(block)
    return md5.hexdigest()


def is_notebook() -> bool:
    """
    Checks if the shell is in a notebook.

    :return: `True` if the shell is for a notebook, `False` otherwise
    """
    try:
        from IPython import get_ipython
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True  # Jupyter notebook or console
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False


def log_message(msg: str, log: logging.Logger, level=logging.INFO, *args, **kwargs):
    """
    Logs a message.

    :param msg: Message to log
    :param log: logger where message should be logged
    :param level: optional log level, defaults to INFO
    :param args: a tuple of arguments passed to the logger
    :param kwargs: a dictionary of keyword arguments passed to the logger
    """
    if is_notebook():
        print(msg)
        log.debug(msg, *args, **kwargs)
    else:
        log.log(level, msg, *args, **kwargs)


def b64encode(b: bytes)->str:
    """
    Returns a string from an iterable collection of bytes.
    """
    encoded = base64.b64encode(b)
    return encoded.decode('utf-8')


def b64decode(s: str)->bytes:
    """
    Returns an iterable collection of bytes representing a base-64 encoding of a given string.
    """
    return base64.decodebytes(s.encode('utf-8'))


def named_dict(obj):
    """
    Returns a named tuple for the given object if it's a dictionary or list;
    otherwise it returns the object itself.
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = named_dict(value)
        return namedtuple('NamedDict', obj.keys())(**obj)
    elif isinstance(obj, list):
        return [named_dict(item) for item in obj]
    else:
        return obj

def decode_JWT(*args, verify):
    """
    thin wrapper around jwt.decode. This function exists for better error handling of the
    jwt exceptions.
    """
    invalidTokenMsg = 'Your Cortex Token is invalid. For more information, go to Cortex Docs > Cortex Tools > Access'
    expiredTokenMsg = 'Your Cortex Token has expired. For more information, go to Cortex Docs > Cortex Tools > Access'
    try:
        decodedJWT = jwt.decode(*args, verify=verify)
        # there are places in the sdk where we try to decode 'any ol token' before sending the token to kong to get verified
        # therefore, here we have some reasonable checks to make sure that this is a cortex token by checking the JWT keys exist
        if not decodedJWT.get('tenant') or not decodedJWT.get('sub') or not decodedJWT.get('exp'):
            raise BadTokenException(invalidTokenMsg)
        if datetime.today().timestamp() > decodedJWT['exp']:
            raise jwt.ExpiredSignatureError
        return decodedJWT
    except jwt.ExpiredSignatureError:
        raise BadTokenException(expiredTokenMsg)
    except jwt.exceptions.InvalidTokenError:
        raise BadTokenException(invalidTokenMsg)
