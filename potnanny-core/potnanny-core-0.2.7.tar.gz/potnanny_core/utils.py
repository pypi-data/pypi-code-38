import os
import re
import copy
import datetime
import subprocess
import logging
import unicodedata
from importlib.machinery import SourceFileLoader

logger = logging.getLogger(__name__)


def reduce_float(f):
    """
    Reduce a float to only 1 decimal place

    args:
        - float
    returns:
        float
    """

    return float("%0.1f" % f)


def convert_celsius(val, reduce=True):
    """
    convert celsius to fahrenheit

    args:
        - int or float
        - bool: Reduce/round floats to only 1 decimal place? (default=True)

    returns:
        a float
    """

    f = float(val) * 1.8 + 32
    if reduce:
        return reduce_float(f)
    else:
        return f


def convert_fahrenheit(val, reduce=True):
    """
    convert fahrenheit to celsius

    args:
        - int or float
        - bool: Reduce/round floats to only 1 decimal place? (default=True)

    returns:
        a float
    """

    c = (float(val) - 32) / 1.8
    if reduce:
        return reduce_float(c)
    else:
        return c


def datetime_for_js(obj):
    """
    Convert a datetime object to format that javascript can handle.

    args:
        - datetime object
    returns:
        str
    raises:
        TypeError if arg is not a DateTime
    """

    if hasattr(obj, 'isoformat'):
        obj = obj.replace(tzinfo=datetime.timezone.utc)
        return obj.isoformat()
    else:
        raise TypeError("Expected a Datetime. Got {}".format(type(obj)))


def rehydrate_plugin_instance(parent_class, class_name, options):
    """
    rehydrate an instance of a plugin based on JSON data

    as I document this, I wonder if it might be better to pickle the objects and
    store them in the db that way? I will consider this...

    args:
        - the parent class the child instance inherits from. Usually either
          ActionPluginBase or BlePluginBase.
        - the class name of the child we are rehydrating
        - init options for the child instance
    returns:
        an instance of a class, or None if instance could not be created.
    raises:
        none
    """
    for plugin in parent_class.plugins:
        if plugin.__name__ == class_name:
            obj = plugin(**options)
            return obj

    return None


def subprocess_cmd(cmd, shell=False):
    """
    run a system command as a subprocess

    args:
        - list (commands, like ['ls','-la'])
        - bool, Run with shell.
          If set to true, the command list will be flattened to a string.
    returns:
        tuple (exit-code, stdout, stderr)
    raises:
        none
    """

    # cast all values to str, because ints will cause errors
    if type(cmd) is list:
        cmd = [str(c) for c in cmd]

    # with shell=True, we flatten commands to a str
    if shell is True and type(cmd) is list:
        cmd = " ".join(cmd)

    child = subprocess.Popen(cmd, shell=shell,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output, errors = child.communicate()
    return (child.returncode, output, errors)


def load_plugins(path):
    """
    Load any plugin files from the named path.

    Yes, arbitrarily loading source files found lying around in filesystem is
    a risky thing. But, our ecosystem is quite closed so, -meh-

    "Strange women lying in ponds distributing swords is no basis for a
    system of government!"

    args:
        - str (a folder path)
    returns:
        none
    raises:
        none
    """
    if not path:
        raise ValueError("path required for plugin loader")

    if not os.path.exists(path):
        raise RuntimeError("path {} not found".format(path))

    files = [f for f in os.listdir(path)
                if f.endswith('.py') and f not in ['__init__.py']]

    for f in files:
        mod = f.split(".")[0]
        fname = os.path.join(path, f)
        try:
            result = SourceFileLoader(mod, fname).load_module()
        except Exception:
            logger.exception("failed to load '{}'".format(fname))

    return


def blescan_devices():
    """
    Scan for all BLE devices.

    args:
        none
    returns:
        list (like: [{'name': NAME, 'address': ADDRESS}, ])
    """

    logger.debug("scanning BLE devices")
    command = ['sudo', 'blescan', '-a']
    rval, output, errors = subprocess_cmd(command, False)
    if not rval:
        buf = clean_blescan_output(output)
        return parse_blescan_buffer(buf)
    else:
        logger.warning("blescan_devices(): {}".format(errors))
        return None


def clean_blescan_output(buf):
    """
    Clean escape chars and hex chars from the output of the blescan cmd.

    args:
        - str (a block of binary-like text)
    return:
        list
    """

    results = []
    for line in buf.splitlines():
        ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')
        clean = line.decode("utf-8")
        clean = ansi_escape.sub('', clean)
        results.append(clean)

    return results


def parse_blescan_buffer(data):
    """
    parse the blescan stdout buffer and extract valid device names/addresses

    args:
        - list (*sanitized* lines from the output of the blescan command)
    returns:
        list (like [{'address': ADDRESS, 'name': NAME}, ])
    """

    devices = []
    buf = {}
    for line in data:
        if re.search(r'^\s*Device', line):
            if buf:
                devices.append(copy.deepcopy(buf))
                buf = {}

            match = re.search(r'(?P<address>\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2})', line)
            if match:
                buf['address'] = match.group('address')
                continue

        match = re.search(r"^\s*Complete Local Name: '(?P<name>.+)'", line)
        if match:
            buf['name'] = match.group('name')

    # one last check of the buffer
    if buf:
        devices.append(copy.deepcopy(buf))

    return devices


def eval_condition(val, stmt):
    """
    Evaluate a conditional str statement against a value.
    like;
        (22, "value gt 80") (False)

    args:
        - float (our reference value)
        - str (a conditional statement, like "value lt 100")
    returns:
        bool
    raises:
        none
    """

    atoms = re.split(r'\s+', stmt)
    if atoms[0] == 'value':
        atoms = atoms[1:]

    oper, threshold = atoms
    threshold = float(threshold)

    if oper == 'lt' and val < threshold:
        return True
    elif oper == 'le' and val <= threshold:
        return True
    elif oper == 'gt' and val > threshold:
        return True
    elif oper == 'ge' and val >= threshold:
        return True
    elif oper == 'eq' and val == threshold:
        return True
    elif oper == 'ne' and val != threshold:
        return True

    return False
