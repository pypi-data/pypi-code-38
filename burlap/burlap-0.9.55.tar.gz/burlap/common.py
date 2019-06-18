from __future__ import with_statement, print_function

import os
import re
import sys
import imp
import types
import copy
import tempfile
import time
import importlib
import warnings
import glob
import pipes
import json
import getpass
import subprocess
import uuid
import inspect
from collections import namedtuple, OrderedDict
from pprint import pprint
from functools import partial
#from datetime import date

import six
from six import StringIO

import yaml

from fabric.api import (
    env,
    local,
    put as __put,
    get as __get,
    run as _run,
    settings,
    sudo as _sudo,
    hide,
#    runs_once,
    local as _local,
)
from fabric.contrib import files
from fabric import state
import fabric.api

from .constants import *
from .utils import get_file_hash
from .shelf import Shelf
from .decorators import task

if hasattr(fabric.api, '_run'):
    _run = fabric.api._run

if hasattr(fabric.api, '_sudo'):
    _sudo = fabric.api._sudo

_tmp_BURLAP_COMMAND_PREFIX = None

BURLAP_COMMAND_PREFIX = int(os.environ.get('BURLAP_COMMAND_PREFIX', '1'))

OS = namedtuple('OS', ['type', 'distro', 'release'])

ROLE_DIR = 'roles'

default_env = None

def init_env():
    """
    Populates the global env variables with custom default settings.
    """
    env.ROLES_DIR = ROLE_DIR
    env.services = []
    env.confirm_deployment = False
    env.is_local = None
    env.base_config_dir = '.'
    env.src_dir = 'src' # The path relative to fab where the code resides.
    env.sites = {} # {site:site_settings}
    env[SITE] = None
    env[ROLE] = None

    env.hosts_retriever = None
    env.hosts_retrievers = type(env)() #'default':lambda hostname: hostname,

    env.hostname_translator = 'default'
    env.hostname_translators = type(env)()
    env.hostname_translators.default = lambda hostname: hostname

    env.default_site = None

    # A list of all site names that should be available on the current host.
    env.available_sites = []

    # A list of all site names per host.
    # {hostname: [sites]}
    # If no entry found, will use available_sites.
    env.available_sites_by_host = {}

    # The command run to determine the percent of disk usage.
    env.disk_usage_command = "df -H | grep -vE '^Filesystem|tmpfs|cdrom|none' | awk '{print $5 " " $1}'"

    env.burlap_data_dir = '.burlap'

    env.setdefault('roledefs', {})
    env.setdefault('roles', [])
    env.setdefault('hosts', [])
    env.setdefault('exclude_hosts', [])


if 'services' not in env:
    default_env = env.copy()
    init_env()

env[SITE] = None
env[ROLE] = None

# If true, prevents run() from executing its command.
_dryrun = False

# If true, causes output of more debugging info.
_verbose = False

_show_command_output = True

state_variables = [
    'required_system_packages',
    'required_python_packages',
    'required_ruby_packages',

    'service_configurators',
    'service_pre_deployers',
    'service_pre_db_dumpers',
    'service_deployers',
    'service_post_deployers',
    'service_post_db_loaders',
    'service_restarters',
    'service_stoppers',
    'services',

    'manifest_recorder',
    'manifest_comparer',
    'manifest_deployers',
    'manifest_deployers_befores',
    'manifest_deployers_takes_diff',

    'post_callbacks',
    'post_role_load_callbacks',

    'post_import_modules',

    'all_satchels',

    'runs_once_methods',
]

required_system_packages = type(env)() # {service:{os:[packages]}
required_python_packages = type(env)() # {service:{os:[packages]}
required_ruby_packages = type(env)() # {service:{os:[packages]}

service_configurators = type(env)() # {service:[func]}
service_pre_deployers = type(env)() # {service:[func]}
service_pre_db_dumpers = type(env)() # {service:[func]}
service_deployers = type(env)() # {service:[func]}
service_post_deployers = type(env)() # {service:[func]}
service_post_db_loaders = type(env)() # {service:[func]}
service_restarters = type(env)() # {service:[func]}
service_stoppers = type(env)() # {service:[func]}
services = {} # {name: service_obj}

manifest_recorder = type(env)() #{component:[func]}
manifest_comparer = type(env)() #{component:[func]}
manifest_deployers = type(env)() #{component:[func]}
manifest_deployers_befores = type(env)() #{component:[pending components that must be run first]}
#manifest_deployers_afters = type(env)() #{component:[pending components that must be run last]}
manifest_deployers_takes_diff = type(env)()

post_callbacks = []
post_role_load_callbacks = []

runs_once_methods = []

post_import_modules = set()

all_satchels = {}

SATCHEL_NAME_PATTERN = re.compile(r'^[a-z][a-z0-9]*$')

# CMD_VAR_REGEX = re.compile(r'(?:^|[^{]+)(?<!\\){([^{}]+)}')
#CMD_VAR_REGEX = re.compile(r'(?:^|[^{\\]+){([^{}]+)}')
CMD_VAR_REGEX = re.compile(r'(?<!\{){([^\{\}]+)}')
CMD_ESCAPED_VAR_REGEX = re.compile(r'\{{2}[^\{\}]+\}{2}')

def get_state():
    d = {}
    for k in state_variables:
        v = globals()[k]
        if isinstance(v, (dict, set)):
            v = v.copy()
        elif isinstance(v, list):
            v = list(v)
        else:
            raise NotImplementedError('State variable %s has unknown type %s' % (k, type(v)))
        d[k] = v
    return d

def clear_state():
    d = {}
    for k in state_variables:
        v = globals()[k]
        if isinstance(v, (set, dict)):
            v.clear()
        elif isinstance(v, list):
            while v:
                v.pop()
        else:
            raise NotImplementedError('State variable %s has unknown type %s' % (k, type(v)))

def set_state(d):
    assert isinstance(d, dict), 'State must be a dictionary.'
    for k in state_variables:
        v = d[k]
        if isinstance(v, (set, dict)):
            globals()[k].update(v)
        elif isinstance(v, list):
            globals()[k].extend(v)
        else:
            raise NotImplementedError('State variable %s has unknown type %s' % (k, type(v)))

def deprecation(message):
    warnings.warn(message, DeprecationWarning, stacklevel=2)

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def start_error():
    print(Colors.FAIL)

def end_error():
    print(Colors.ENDC)

def fail_str(s):
    return Colors.FAIL + str(s) + Colors.ENDC

def success_str(s):
    return Colors.OKGREEN + str(s) + Colors.ENDC

def print_fail(s, file=None): # pylint: disable=redefined-builtin
    print(fail_str(s), file=file or sys.stderr)

def print_success(s, file=None): # pylint: disable=redefined-builtin
    print(success_str(s), file=file or sys.stdout)

def create_module(name, code=None):
    """
    Dynamically creates a module with the given name.
    """

    if name not in sys.modules:
        sys.modules[name] = imp.new_module(name)

    module = sys.modules[name]

    if code:
        print('executing code for %s: %s' % (name, code))
        exec(code in module.__dict__) # pylint: disable=exec-used
        exec("from %s import %s" % (name, '*')) # pylint: disable=exec-used

    return module

#http://www.saltycrane.com/blog/2010/09/class-based-fabric-scripts-metaprogramming-hack/
#http://stackoverflow.com/questions/3799545/dynamically-importing-python-module/3799609#3799609
def add_class_methods_as_module_level_functions_for_fabric(instance, module_name, method_name, module_alias=None):
    '''
    Utility to take the methods of the instance of a class, instance,
    and add them as functions to a module, module_name, so that Fabric
    can find and call them. Call this at the bottom of a module after
    the class definition.
    '''
    import imp
    from .decorators import task_or_dryrun

    # get the module as an object
    module_obj = sys.modules[module_name]

    module_alias = re.sub('[^a-zA-Z0-9]+', '', module_alias or '')

    # Iterate over the methods of the class and dynamically create a function
    # for each method that calls the method and add it to the current module
    # NOTE: inspect.ismethod actually executes the methods?!
    #for method in inspect.getmembers(instance, predicate=inspect.ismethod):

    method_obj = getattr(instance, method_name)

    if not method_name.startswith('_'):

        # get the bound method
        func = getattr(instance, method_name)

#         if module_name == 'buildbot' or module_alias == 'buildbot':
#             print('-'*80)
#             print('module_name:', module_name)
#             print('method_name:', method_name)
#             print('module_alias:', module_alias)
#             print('module_obj:', module_obj)
#             print('func.module:', func.__module__)

        # Convert executable to a Fabric task, if not done so already.
        if not hasattr(func, 'is_task_or_dryrun'):
            func = task_or_dryrun(func)

        if module_name == module_alias \
        or (module_name.startswith('satchels.') and module_name.endswith(module_alias)):

            # add the function to the current module
            setattr(module_obj, method_name, func)

        else:

            # Dynamically create a module for the virtual satchel.
            _module_obj = module_obj
            module_obj = create_module(module_alias)
            setattr(module_obj, method_name, func)
            post_import_modules.add(module_alias)

        fabric_name = '%s.%s' % (module_alias or module_name, method_name)
        func.wrapped.__func__.fabric_name = fabric_name

        return func

def str_to_list(s):
    """
    Converts a string of comma delimited values and returns a list.
    """
    if s is None:
        return []
    if isinstance(s, (tuple, list)):
        return s
    if not isinstance(s, six.string_types):
        raise NotImplementedError('Unknown type: %s' % type(s))
    return [_.strip().lower() for _ in (s or '').split(',') if _.strip()]

def assert_valid_satchel(name):
    name = name.strip().upper()
    assert name in all_satchels, 'Invalid satchel: %s' % name
    return name

def clean_service_name(name):
    name = (name or '').strip().lower()
    return name

def str_to_component_list(s):
    lst = [clean_service_name(name) for name in str_to_list(s)]
    return lst

def add_deployer(event, func, before=None, after=None, takes_diff=False):

    before = before or []

    after = after or []

    event = event.strip().upper()

    manifest_deployers.setdefault(event, [])
    if func not in manifest_deployers[event]:
        manifest_deployers[event].append(func)

    manifest_deployers_befores.setdefault(event, [])
    manifest_deployers_befores[event].extend(map(str.upper, before))

    for _c in after:
        _c = _c.strip().upper()
        manifest_deployers_befores.setdefault(_c, [])
        manifest_deployers_befores[_c].append(event)

    manifest_deployers_takes_diff[func] = takes_diff

def resolve_deployer(func_name):

    if '.' in func_name:
        mod_name, func_name = func_name.split('.')
    else:
        mod_name = 'fabfile'

    if mod_name.upper() in all_satchels:
        ret = all_satchels[mod_name.upper()].configure
    else:
        ret = getattr(importlib.import_module(mod_name), func_name)

    return ret

class Deployer:
    """
    Represents a task that must be run to update a service after a configuration change
    has been made.
    """

    def __init__(self, func, before=None, after=None, takes_diff=False):
        self.func = func
        self.before = before or []
        self.after = after or []
        self.takes_diff = takes_diff

def get_class_module_name(self):
    name = self.__module__
    if name == '__main__':
        filename = sys.modules[self.__module__].__file__
        name = os.path.splitext(os.path.basename(filename))[0]
    return name

class _EnvProxy:
    """
    Filters a satchel's access to the environment object.

    Allows referencing of environment variables without explicitly specifying
    the Satchel's namespace.

    For example, instead of:

        env.satchelname_variable = 123

    you can use:

        self.env.variable = 123
    """

    def __init__(self, satchel):
        self.satchel = satchel

    def __contains__(self, k):
        k = self.satchel.env_prefix + k
        return k in env

    def __getitem__(self, k):
        return getattr(self, k)

    def __getattr__(self, k):
        if k in ('satchel',):
            return object.__getattribute__(self, k)
        return env.get(self.satchel.env_prefix + k)

    def __setattr__(self, k, v):
        if k in ('satchel',):
            return object.__setattr__(self, k, v)
        env[self.satchel.env_prefix + k] = v

def is_local():
    env.is_local = env.host_string in ('localhost', '127.0.0.1')
    return env.is_local

def format(s, lenv, genv, prefix=None, ignored_variables=None): # pylint: disable=redefined-builtin

    verbose = get_verbose()

    ignored_variables = set(ignored_variables or [])

    # Resolve all variable names.
    cnt = 0
    while 1:
        cnt += 1
        if cnt > 10:
            raise Exception('Too many variables containing variables.')

        var_names = CMD_VAR_REGEX.findall(s)
#         if verbose:
#             print('format.s:', s)
#             print('found var_names:', var_names)

        if not var_names:
            break
        elif set(var_names).issubset(ignored_variables):
            break

        # Lookup local and global variable values.
        var_values = {}
        for var_name in var_names:
            if var_name in ignored_variables:
                continue
            elif var_name in lenv:
                # Find local variable name in local namespace.
                if verbose:
                    print('Found %s in lenv.' % var_name)
                var_values[var_name] = lenv[var_name]
            elif var_name in genv:
                # Find prefixed variable in global namespace.
                if verbose:
                    print('Found %s in genv.' % var_name)
                var_values[var_name] = genv[var_name]
            elif prefix and prefix+'_'+var_name in genv:
                # Find unprefixed variable in global namespace.
                if verbose:
                    print('Found prefix+%s in genv.' % var_name)
                var_values[var_name] = genv[prefix+'_'+var_name]
            elif prefix and var_name.startswith(prefix+'_') and var_name[len(prefix+'_'):] in lenv:
                # Find prefixed variable in local namespace.
                if verbose:
                    print('Found prefix-%s in genv.' % var_name)
                var_values[var_name] = lenv[var_name[len(prefix+'_'):]]
            else:
                raise Exception((
                    'Command "%s" references variable "%s" which is not found '
                    'in either the local or global namespace.') % (s, var_name))

        escaped_var_names = dict(
            (k, str(uuid.uuid4()))
            for k in CMD_ESCAPED_VAR_REGEX.findall(s)
        )
        for k, v in escaped_var_names.items():
            s = s.replace(k, v)

        for _vn in ignored_variables:
            # We can't escape ignroed variables this way, because the variables may use Python ":" operator,
            # conflicting with curly brace string interpolation.
            k = '{%s}' % _vn
            v = str(uuid.uuid4())
            escaped_var_names[k] = v
            s = s.replace(k, v)

        s = s.format(**var_values)

        for k, v in escaped_var_names.items():
            s = s.replace(v, k)

    s = s.replace(r'\{', '{')
    s = s.replace(r'\}', '}')

    return s

class Renderer:
    """
    Base convenience wrapper around command executioners.
    """

    env_type = None

    def __init__(self, obj, lenv=None, set_default=False):
        from fabric.context_managers import env

        # Satchel instance.
        self.obj = obj

        # Copy the local environment dictionary so we don't modify the original.
        self.lenv = type(env)(obj.lenv if lenv is None else lenv)

        self.genv = env#type(env)(obj.genv)

        # If true, getattr will return None if no attribute set.
        self._set_default = set_default

    def format(self, s, **kwargs):
        return format(s, lenv=self.lenv, genv=self.genv, prefix=self.obj.name.lower(), **kwargs)

    def render_to_string(self, *args, **kwargs):
        format = kwargs.pop('format', True)
        kwargs['extra'] = self.collect_genv(include_local=True, include_global=False)
        s = self.obj.render_to_string(*args, **kwargs)
        if format:
            s = self.format(s)
        return s

    def collect_genv(self, include_local=True, include_global=True):
        """
        Returns a copy of the global environment with all the local variables copied back into it.
        """
        e = type(self.genv)()
        if include_global:
            e.update(self.genv)
        if include_local:
            for k, v in self.lenv.items():
                e['%s_%s' % (self.obj.name.lower(), k)] = v
        return e

    def __getitem__(self, key):
        return getattr(self, key)

    def __getattr__(self, attrname):

        # Alias .env to the default type.
        if attrname == 'env':
            attrname = self.env_type

        if attrname in ('obj', 'lenv', 'genv', 'env_type', '_set_default'):
            return object.__getattribute__(self, attrname)

        def wrap(func):

            def _wrap(cmd, *args, **kwargs):
                cmd = self.format(cmd)
                return func(cmd, *args, **kwargs)

            return _wrap

        def wrap2(func):
            # For non-command functions, just pass-through.

            def _wrap(*args, **kwargs):
                return func(*args, **kwargs)

            return _wrap

        def put_wrap2(func):
            # For non-command functions, just pass-through.

            def _wrap(*args, **kwargs):
                kwargs.setdefault('remote_path', kwargs.get('local_path'))
                kwargs['local_path'] = self.format(kwargs['local_path'])
                kwargs['remote_path'] = self.format(kwargs['remote_path'])
                return func(*args, **kwargs)

            return _wrap

        def install_config_wrap(func):
            # For non-command functions, just pass-through.

            def _wrap(*args, **kwargs):
                kwargs.setdefault('remote_path', kwargs.get('local_path'))
                kwargs['local_path'] = self.format(kwargs['local_path'])
                kwargs['remote_path'] = self.format(kwargs['remote_path'])
                kwargs['formatter'] = self.format
                return func(*args, **kwargs)

            return _wrap

        def sed_wrap2(func):
            # For non-command functions, just pass-through.

            def _wrap(*args, **kwargs):
                kwargs['filename'] = self.format(kwargs['filename'])
                return func(*args, **kwargs)

            return _wrap

        def append_wrap2(func):
            # For non-command functions, just pass-through.

            def _wrap(*args, **kwargs):
                args = list(args)

                if len(args) >= 1:
                    args[0] = self.format(args[0])
                else:
                    kwargs['text'] = self.format(kwargs['text'])

                if len(args) >= 2:
                    args[1] = self.format(args[1])
                else:
                    kwargs['filename'] = self.format(kwargs['filename'])

                return func(*args, **kwargs)

            return _wrap

        try:
            ret = getattr(self.obj, attrname)
        except AttributeError:
            try:
                return getattr(self.lenv, attrname)
            except AttributeError:
                try:
                    return getattr(self.genv, attrname)
                except AttributeError:
                    if self._set_default:
                        return
                    raise

        # If we're calling a command executor, wrap it so that it automatically formats
        # the command string using our preferred environment dictionary when called.
        if attrname.startswith('local') \
        or attrname.startswith('_local') \
        or attrname.startswith('run') \
        or attrname.startswith('run_or_local') \
        or attrname.startswith('_run') \
        or attrname.startswith('comment') \
        or attrname.startswith('pc') \
        or attrname.startswith('sudo') \
        or attrname.startswith('sudo_or_local'):
            ret = wrap(ret)
        elif attrname.startswith('reboot'):
            ret = wrap2(ret)
        elif attrname.startswith('put') \
        or attrname.startswith('install_script') \
        or attrname.startswith('install_config'):
            ret = put_wrap2(ret)
        elif attrname.startswith('install_config'):
            ret = install_config_wrap(ret)
        elif attrname.startswith('sed'):
            ret = sed_wrap2(ret)
        elif attrname.startswith('append'):
            ret = append_wrap2(ret)

        return ret

class LocalRenderer(Renderer):

    env_type = 'lenv'

class GlobalRenderer(Renderer):

    env_type = 'genv'

def get_satchel(name):
    return all_satchels[name.strip().upper()]

def reset_all_satchels():
    for name, satchel in all_satchels.items():
        satchel.clear_caches()

def is_callable(obj, name):
    """
    A version of callable() that doesn't execute properties when doing the test for callability.
    """
    return callable(getattr(obj.__class__, name, None))

class Satchel:
    """
    Represents a base unit of functionality that is deployed and maintained on one
    or more a target servers.
    """

    # This will be used to uniquely identify this unit of functionality.
    name = None

    # This is the list of Fabric tasks exposed by the instance.
    tasks = []

    required_system_packages = {
        #OS: [package1, package2, ...],
    }

    # These files will have their changes tracked.
    # You can specify dynamic values by using brace notation to refer to a satchel variable.
    # e.g. templates = ['{my_conf_template}']
    templates = []

    def __init__(self):
        assert self.name, 'A name must be specified.'
        self.name = self.name.strip().lower()

        assert SATCHEL_NAME_PATTERN.findall(self.name), 'Invalid name: %s' % self.name

        self._os_version_cache = {} # {host:info}

        # Global environment.
        self.genv = env

        self._genv = None

        self._requires_satchels = set()

        self.env = _EnvProxy(self)

        self.files = files

        self._local_renderer = None

        self._last_manifest = None

        self.settings = settings

        self._set_defaults()

        self._verbose = None

        self.register()

        # Add built-in tasks.
        if 'install_packages' not in self.tasks:
            self.tasks += ('install_packages',)
        if 'configure' not in self.tasks:
            self.tasks += ('configure',)

        # Register select instance methods as Fabric tasks.
        for task_name in self.get_tasks():
            task = add_class_methods_as_module_level_functions_for_fabric(
                instance=self,
                module_name=get_class_module_name(self),
                method_name=task_name,
                module_alias=self.name,
            )

            # If task is marked as a deployer, then add it to the deployer list.
            if hasattr(task.wrapped, 'is_deployer') or task_name == 'configure':
                add_deployer(
                    event=self.name,
                    func=task.wrapped.fabric_name,#deployer.func,
                    before=getattr(task.wrapped, 'deploy_before', []),#deployer.before,
                    after=getattr(task.wrapped, 'deploy_after', []),#deployer.after,
                    takes_diff=getattr(task.wrapped, 'deployer_takes_diff', False))

            # Collect callbacks to run after basic satchel init is complete.
            if hasattr(task.wrapped, 'is_post_callback'):
                post_callbacks.append(task.wrapped)

        deployers = self.get_deployers()
        if deployers:
            for deployer in deployers:
                assert isinstance(deployer, Deployer), 'Invalid deployer "%s".' % deployer
                add_deployer(
                    event=self.name,
                    func=deployer.func,
                    before=deployer.before,
                    after=deployer.after,
                    takes_diff=deployer.takes_diff)

    def _set_defaults(self):
        """
        Wrapper around the overrideable set_defaults().
        """

        # Register an "enabled" flag on all satchels.
        # How this flag is interpreted depends on the individual satchel.
        _prefix = '%s_enabled' % self.name
        if _prefix not in env:
            env[_prefix] = True

        # Do a one-time init of custom defaults.
        _key = '_%s' % self.name
        if _key not in env:
            env[_key] = True
            self.set_defaults()

    @staticmethod
    def reset_all_satchels():
        reset_all_satchels()

    @staticmethod
    def is_callable(*args, **kwargs):
        return is_callable(*args, **kwargs)

    def clear_caches(self):
        self._local_renderer = None
        self._last_manifest = None
        self._os_version_cache = {}

    @property
    def new_local_renderer(self):
        self._local_renderer = None
        return self.local_renderer

    def capture_bash(self):
        """
        Context manager that hides the command prefix and activates dryrun to capture all following task commands to their equivalent Bash outputs.
        """
        class Capture:

            def __init__(self, satchel):
                self.satchel = satchel
                self._dryrun = self.satchel.dryrun
                self.satchel.dryrun = 1
                begincap()
                self._stdout = sys.stdout
                self._stderr = sys.stderr
                self.stdout = sys.stdout = StringIO()
                self.stderr = sys.stderr = StringIO()

            def __enter__(self):
                return self

            def __exit__(self, type, value, traceback): # pylint: disable=redefined-builtin
                endcap()
                self.satchel.dryrun = self._dryrun
                sys.stdout = self._stdout
                sys.stderr = self._stderr

        return Capture(self)

    def register(self):
        """
        Adds this satchel to the global registeries for fast lookup from other satchels.
        """

        self._set_defaults()

        all_satchels[self.name.upper()] = self

        manifest_recorder[self.name] = self.record_manifest

        # Register service commands.
        if self.required_system_packages:
            required_system_packages[self.name.upper()] = self.required_system_packages

    def unregister(self):
        """
        Removes this satchel from global registeries.
        """

        for k in list(env.keys()):
            if k.startswith(self.env_prefix):
                del env[k]

        try:
            del all_satchels[self.name.upper()]
        except KeyError:
            pass

        try:
            del manifest_recorder[self.name]
        except KeyError:
            pass

        try:
            del manifest_deployers[self.name.upper()]
        except KeyError:
            pass

        try:
            del manifest_deployers_befores[self.name.upper()]
        except KeyError:
            pass

        try:
            del required_system_packages[self.name.upper()]
        except KeyError:
            pass

    @property
    def is_local(self):
        return is_local()

    @property
    def current_hostname(self):
        return get_current_hostname()

    def set_site(self, site):
        set_site(site)

    def set_role(self, role):
        set_role(role)

    def get_tasks(self):
        """
        Returns an ordered list of all task names.
        """
        tasks = set(self.tasks)#DEPRECATED
        for _name in dir(self):
            # Skip properties so we don't accidentally execute any methods.
            if isinstance(getattr(type(self), _name, None), property):
                continue
            attr = getattr(self, _name)
            if hasattr(attr, '__call__') and getattr(attr, 'is_task', False):
                tasks.add(_name)
        return sorted(tasks)

    #DEPRECATED
    def push_genv(self):
        self._genv = type(self.genv)(self.genv.copy())

    #DEPRECATED
    def pop_genv(self):
        if self._genv is not None:
            _genv = self._genv
            self.genv = type(self._genv)(self._genv.copy())
            self._genv = None
            return _genv

    def add_post_role_load_callback(self, cb):
        post_role_load_callbacks.append(cb)

    @task
    def list_tasks(self):
        for _task in self.get_tasks():
            print(_task)

    def create_local_renderer(self):
        """
        Instantiates a new local renderer.
        Override this to do any additional initialization.
        """
        r = LocalRenderer(self)
        return r

    @property
    def local_renderer(self):
        """
        Retrieves the cached local renderer.
        """
        if not self._local_renderer:
            r = self.create_local_renderer()
            self._local_renderer = r
        return self._local_renderer

    def clear_local_renderer(self):
        """
        Deletes the cached local renderer.
        """
        self._local_renderer = None

    @property
    def global_renderer(self):
        return GlobalRenderer(self)

    @property
    def all_satchels(self):
        return all_satchels

    @property
    def all_other_enabled_satchels(self):
        """
        Returns a dictionary of satchels used in the current configuration, excluding ourselves.
        """
        return dict(
            (name, satchel)
            for name, satchel in self.all_satchels.items()
            if name != self.name.upper() and name.lower() in map(str.lower, self.genv.services)
        )

    def iter_sites(self, *args, **kwargs):
        kwargs.setdefault('verbose', self.verbose)
        return iter_sites(*args, **kwargs)

    def load_site(self, role=None, site=None):
        if hasattr(role, 'role'):
            role = role.role
        return RoleLoader(role=role or env[ROLE], site=site)

    @property
    def is_selected(self):
        return self.name.lower() in self.genv.services

    def get_satchel(self, name):
        return get_satchel(name)

    def define_cron_job(self, template, script_path=None, command=None, name=None, perms='600', user='root', schedule='* * * * *'):
        assert name, 'No name specified!'
        if 'cron' not in self.env:
            self.env.cron = type(env)()
        self.env.cron[name] = type(env)()
        self.env.cron[name].template = '%s/%s' % (self.name, template)

        script_path = script_path or ('/etc/cron.d/%s' % name)
        self.env.cron[name].script_path = script_path

        self.env.cron[name].command = command
        self.env.cron[name].perms = '600'
        self.env.cron[name].user = user
        self.env.cron[name].schedule = schedule
        self.templates = list(self.templates)
        self.templates.append(template)

    def install_cron_job(self, name='default', extra=None):
        assert name in self.env.cron

        data = type(env)(self.env.cron[name].copy())
        data.update(extra or {})

        self.install_script(
            local_path=data.template,
            remote_path=data.script_path,
            render=True,
            extra=data,
        )

        r = self.local_renderer

        r.sudo('chown root:root %s' % data.script_path)

        # Must be 600, otherwise gives INSECURE MODE error.
        # http://unix.stackexchange.com/questions/91202/cron-does-not-print-to-syslog
        r.sudo('chmod %s %s' % (data.perms, data.script_path))#env.put_remote_path)
        r.sudo('service cron restart')

    def uninstall_cron_job(self, name):
        assert name in self.cron

    def pc(self, *args, **kwargs):
        return pc(*args, **kwargs)

    def requires_satchel(self, satchel):
        self._requires_satchels.add(satchel.name.lower())

    def check_satchel_requirements(self):
        lst = []
        lst.extend(self.genv.get('services') or [])
        lst.extend(self.genv.get('satchels') or [])
        lst = [_.lower() for _ in lst]
        for req in self._requires_satchels:
            req = req.lower()
            assert req in lst

    @property
    def lenv(self):
        """
        Returns a version of env filtered to only include the variables in our namespace.
        """
        _env = type(env)()
        for _k, _v in six.iteritems(env):
            if _k.startswith(self.name+'_'):
                _env[_k[len(self.name)+1:]] = _v
        return _env

    @property
    def env_prefix(self):
        return '%s_' % self.name

    @property
    def packager(self):
        return get_packager()

    @property
    def os_version(self):
        hs = env.host_string
        if hs not in self._os_version_cache:
            self._os_version_cache[hs] = get_os_version()
        return self._os_version_cache[hs]

    def param_changed_to(self, key, to_value, from_value=None):
        """
        Returns true if the given parameter, with name key, has transitioned to the given value.
        """
        last_value = getattr(self.last_manifest, key)
        current_value = self.current_manifest.get(key)
        if from_value is not None:
            return last_value == from_value and current_value == to_value
        return last_value != to_value and current_value == to_value

    def sleep(self, seconds):
        if self.dryrun:
            cmd = 'sleep %s' % seconds
            if BURLAP_COMMAND_PREFIX:
                print('%s local: %s' % (render_command_prefix(), cmd))
            else:
                print(cmd)
        else:
            time.sleep(seconds)

    def _local(self, *args, **kwargs):
        return _local(*args, **kwargs)

    def _run(self, *args, **kwargs):
        return _run(*args, **kwargs)

    def render_to_string(self, *args, **kwargs):
        return render_to_string(*args, **kwargs)

    def reboot_or_dryrun(self, *args, **kwargs):
        """
        Reboots the server and waits for it to come back.
        """
        warnings.warn('Use self.run() instead.', DeprecationWarning, stacklevel=2)
        self.reboot(*args, **kwargs)

    @task
    def reboot(self, *args, **kwargs):
        """
        Reboots the server and waits for it to come back.
        """
        reboot_or_dryrun(*args, **kwargs)

    def enable_attr(self, *args, **kwargs):
        return enable_attribute_or_dryrun(*args, **kwargs)

    def disable_attr(self, *args, **kwargs):
        return disable_attribute_or_dryrun(*args, **kwargs)

    def write_to_file(self, *args, **kwargs):
        return write_to_file(*args, **kwargs)

    def upload_content(self, *args, **kwargs):
        return upload_content(*args, **kwargs)

    def find_template(self, template):
        return find_template(template)

    def get_template_contents(self, template):
        return get_template_contents(template)

    def install_script(self, *args, **kwargs):
        return install_script(*args, **kwargs)

    def install_config(self, *args, **kwargs):
        return install_config(*args, **kwargs)

    def set_site_specifics(self, site):
        """
        Loads settings for the target site.
        """
        r = self.local_renderer
        site_data = self.genv.sites[site].copy()
        r.env.site = site
        if self.verbose:
            print('set_site_specifics.data:')
            pprint(site_data, indent=4)

        # Remove local namespace settings from the global namespace
        # by converting <satchel_name>_<variable_name> to <variable_name>.
        local_ns = {}
        for k, v in list(site_data.items()):
            if k.startswith(self.name + '_'):
                _k = k[len(self.name + '_'):]
                local_ns[_k] = v
                del site_data[k]

        r.env.update(local_ns)
        r.env.update(site_data)

    def vprint(self, *args, **kwargs):
        """
        When verbose is set, acts like the normal print() function.
        Otherwise, does nothing.
        """
        if self.verbose:
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 2)
            caller_name = calframe[1][3]
            prefix = '%s.%s:' % (self.name.lower(), caller_name)
            print(prefix, *args, **kwargs)

    def get_package_list(self):
        """
        Returns a list of all required packages.
        """
        os_version = self.os_version # OS(type=LINUX, distro=UBUNTU, release='14.04')
        self.vprint('os_version:', os_version)

        # Lookup legacy package list.
        # OS: [package1, package2, ...],
        req_packages1 = self.required_system_packages
        if req_packages1:
            deprecation('The required_system_packages attribute is deprecated, '
                'use the packager_system_packages property instead.')

        # Lookup new package list.
        # OS: [package1, package2, ...],
        req_packages2 = self.packager_system_packages

        patterns = [
            (os_version.type, os_version.distro, os_version.release),
            (os_version.distro, os_version.release),
            (os_version.type, os_version.distro),
            (os_version.distro,),
            os_version.distro,
        ]
        self.vprint('req_packages1:', req_packages1)
        self.vprint('req_packages2:', req_packages2)
        package_list = None
        found = False
        for pattern in patterns:
            self.vprint('pattern:', pattern)
            for req_packages in (req_packages1, req_packages2):
                if pattern in req_packages:
                    package_list = req_packages[pattern]
                    found = True
                    break
        if not found:
            print('Warning: No operating system pattern found for %s' % (os_version,))
        self.vprint('package_list:', package_list)
        return package_list

    def install_packages(self):
        """
        Installs all required packages listed for this satchel.
        Normally called indirectly by running packager.configure().
        """
        os_version = self.os_version
        package_list = self.get_package_list()
        if package_list:
            package_list_str = ' '.join(package_list)
            if os_version.distro == UBUNTU:
                self.sudo('apt-get update --fix-missing; DEBIAN_FRONTEND=noninteractive apt-get install --yes %s' % package_list_str)
            elif os_version.distro == DEBIAN:
                self.sudo('apt-get update --fix-missing; DEBIAN_FRONTEND=noninteractive apt-get install --yes %s' % package_list_str)
            elif os_version.distro == FEDORA:
                self.sudo('yum install --assumeyes %s' % package_list_str)
            else:
                raise NotImplementedError('Unknown distro: %s' % os_version.distro)

    def purge_packages(self):
        os_version = self.os_version # OS(type=LINUX, distro=UBUNTU, release='14.04')
#         print('os_version:', os_version)
        req_packages = self.required_system_packages
        patterns = [
            (os_version.type, os_version.distro, os_version.release),
            (os_version.distro, os_version.release),
            (os_version.type, os_version.distro),
            (os_version.distro,),
            os_version.distro,
        ]
#         print('req_packages:', req_packages)
        package_list = None
        for pattern in patterns:
#             print('pattern:', pattern)
            if pattern in req_packages:
                package_list = req_packages[pattern]
                break
#         print('package_list:', package_list)
        if package_list:
            package_list_str = ' '.join(package_list)
            if os_version.distro == UBUNTU:
                self.sudo_or_dryrun('apt-get purge %s' % package_list_str)
            elif os_version.distro == FEDORA:
                self.sudo_or_dryrun('yum remove %s' % package_list_str)
            else:
                raise NotImplementedError('Unknown distro: %s' % os_version.distro)

    def set_defaults(self):
        # Override to specify custom defaults.
        pass

    def render_to_file(self, *args, **kwargs):
        return render_to_file(*args, **kwargs)

    def put_or_dryrun(self, *args, **kwargs):
        warnings.warn('Use self.put() instead.', DeprecationWarning, stacklevel=2)
        return put_or_dryrun(*args, **kwargs)

    def get(self, *args, **kwargs):
        return get_or_dryrun(*args, **kwargs)

    def put(self, *args, **kwargs):
        return put_or_dryrun(*args, **kwargs)

    def rsync(self, **kwargs):
        return rsync_or_dryrun(**kwargs)

    def run_or_dryrun(self, *args, **kwargs):
        warnings.warn('Use self.run() instead.', DeprecationWarning, stacklevel=2)
        return run_or_dryrun(*args, **kwargs)

    @task
    def run(self, *args, **kwargs):
        return run_or_dryrun(*args, **kwargs)

    def run_or_local(self, *args, **kwargs):
        if is_local():
            # By default, Fabric's local() doesn't capture output, so to make it more interchangable with run(),
            # we automatically set capture, even though this will temporarily hide output.
            kwargs['capture'] = True
            return local_or_dryrun(*args, **kwargs)
        return run_or_dryrun(*args, **kwargs)

    @task
    def run_on_all_sites(self, cmd, *args, **kwargs):
        """
        Like run(), but re-runs the command for each site in the current role.
        """
        r = self.local_renderer
        for _site, _data in iter_sites():
            r.env.SITE = _site
            with self.settings(warn_only=True):
                r.run('export SITE={SITE}; export ROLE={ROLE}; '+cmd)

    def local_or_dryrun(self, *args, **kwargs):
        warnings.warn('Use self.local() instead.', DeprecationWarning, stacklevel=2)
        return local_or_dryrun(*args, **kwargs)

    def append(self, *args, **kwargs):
        return append_or_dryrun(*args, **kwargs)

    def file_exists(self, *args, **kwargs):
        return files_exists_or_dryrun(*args, **kwargs)

    def file_contains(self, *args, **kwargs):
        """
        filename text
        http://docs.fabfile.org/en/1.13/api/contrib/files.html#fabric.contrib.files.contains
        """
        from fabric.contrib.files import contains
        return contains(*args, **kwargs)

    def sed(self, *args, **kwargs):
        return sed_or_dryrun(*args, **kwargs)

    def local(self, *args, **kwargs):
        return local_or_dryrun(*args, **kwargs)

    def local_if_missing(self, fn, cmd, **kwargs):
        _cmd = "[ ! -f '%s' ] && %s || true" % (fn, cmd)
        self.local(_cmd, **kwargs)

    def local_if_exists(self, fn, cmd, **kwargs):
        _cmd = "[ -f '%s' ] && %s || true" % (fn, cmd)
        self.local(_cmd, **kwargs)

    def sudo_or_dryrun(self, *args, **kwargs):
        warnings.warn('Use self.sudo() instead.', DeprecationWarning, stacklevel=2)
        return sudo_or_dryrun(*args, **kwargs)

    @task
    def sudo(self, *args, **kwargs):
        return sudo_or_dryrun(*args, **kwargs)

    def sudo_or_local(self, *args, **kwargs):
        if is_local():
            return local_or_dryrun(*args, **kwargs)
        return sudo_or_dryrun(*args, **kwargs)

    def sudo_if_missing(self, fn, cmd, **kwargs):
        _cmd = "[ ! -f '%s' ] && %s || true" % (fn, cmd)
        self.sudo(_cmd, **kwargs)

    def sudo_if_exists(self, fn, cmd, **kwargs):
        _cmd = "[ -f '%s' ] && %s || true" % (fn, cmd)
        self.sudo(_cmd, **kwargs)

    def write_temp_file(self, *args, **kwargs):
        return write_temp_file_or_dryrun(*args, **kwargs)

    def comment(self, *args):
        print('# ' + (' '.join(map(str, args))))

    def print_command(self, *args, **kwargs):
        return print_command(*args, **kwargs)

    def get_templates(self):
        return [_ for _ in list(self.templates or []) if _]

    def get_trackers(self):
        return []

    @task
    def record_manifest(self):
        """
        Returns a dictionary representing a serialized state of the service.
        """
        manifest = get_component_settings(prefixes=[self.name])

        # Record a signature of each template so we know to redeploy when they change.
        for template in self.get_templates():
            # Dereference brace notation. e.g. convert '{var}' to `env[var]`.
            if template and template.startswith('{') and template.endswith('}'):
                template = self.env[template[1:-1]]

            if not template:
                continue

            if template.startswith('%s/' % self.name):
                fqfn = self.find_template(template)
            else:
                fqfn = self.find_template('%s/%s' % (self.name, template))
            assert fqfn, 'Unable to find template: %s/%s' % (self.name, template)
            manifest['_%s' % template] = get_file_hash(fqfn)

        for tracker in self.get_trackers():
            manifest['_tracker_%s' % tracker.get_natural_key_hash()] = tracker.get_thumbprint()

        if self.verbose:
            pprint(manifest, indent=4)

        return manifest

    @property
    def has_changes(self):
        """
        Returns true if at least one tracker detects a change.
        """
        lm = self.last_manifest
        for tracker in self.get_trackers():
            last_thumbprint = lm['_tracker_%s' % tracker.get_natural_key_hash()]
            if tracker.is_changed(last_thumbprint):
                return True
        return False

    def configure(self):
        """
        The standard method called to apply functionality when the manifest changes.
        """
        lm = self.last_manifest
        for tracker in self.get_trackers():
            self.vprint('Checking tracker:', tracker)
            last_thumbprint = lm['_tracker_%s' % tracker.get_natural_key_hash()]
            self.vprint('last thumbprint:', last_thumbprint)
            has_changed = tracker.is_changed(last_thumbprint)
            self.vprint('Tracker changed:', has_changed)
            if has_changed:
                self.vprint('Change detected!')
                tracker.act()

    # List of satchels that should be run before this one during deployments.
    configure.deploy_before = []
    configure.takes_diff = False #DEPRECATED

    #TODO:deprecated, remove?
    def get_deployers(self):
        """
        Returns one or more Deployer instances, representing tasks to run during a deployment.
        """
        #raise NotImplementedError

    @property
    def current_manifest(self):
        from burlap.manifest import manifest
        return manifest.get_current(name=self.name)

    @property
    def last_manifest(self):
        from burlap.manifest import manifest
        if not self._last_manifest:
            self._last_manifest = LocalRenderer(self, lenv=manifest.get_last(name=self.name), set_default=True)
        return self._last_manifest

    @property
    def verbose(self):
        if self._verbose is None:
            return get_verbose()
        return self._verbose

    @verbose.setter
    def verbose(self, v):
        # 1 or True=local verbose only, 2=global verbose, None=clears local
        if v == LOCAL_VERBOSE:
            self._verbose = True
        elif v is None:
            self._verbose = None
        else:
            set_verbose(v)

    @property
    def dryrun(self):
        return get_dryrun()

    @dryrun.setter
    def dryrun(self, v):
        return set_dryrun(v)

class Service:

    name = None

    # If true, any warnings or errors encountered during commands will be ignored.
    ignore_errors = False

    # This command will be automatically run after every deployment.
    post_deploy_command = None #'restart'

    def __init__(self):
        assert self.name
        self.name = self.name.strip().lower()
        service_restarters[self.name.upper()] = [self.restart]
        service_stoppers[self.name.upper()] = [self.stop]
        if self.post_deploy_command:
            service_post_deployers[self.name.upper()] = [getattr(self, self.post_deploy_command)]

        services[self.name.strip().upper()] = self

        #DEPRECATED
        tasks = (
            'start',
            'stop',
            'restart',
            'enable',
            'disable',
            'status',
            'reload',
        )
        for task_name in tasks:
            add_class_methods_as_module_level_functions_for_fabric(
                instance=self,
                module_name=get_class_module_name(self),
                method_name=task_name,
                module_alias=self.name,
            )

    @property
    def commands(self):
        # {action: {os_version_distro: command}}
        key = '%s_service_commands' % self.name
        if key in env:
            return env[key]

        key = 'service_commands'
        r = self.local_renderer
        if key in r.env:
            return r.env[key]

    def get_command(self, action):
        os_version = self.os_version # OS(type=LINUX, distro=UBUNTU, release='14.04')
#         print('os_version:', os_version)
        patterns = [
            (os_version.type, os_version.distro, os_version.release),
            (os_version.distro, os_version.release),
            (os_version.type, os_version.distro),
            (os_version.distro,),
            os_version.distro,
        ]
        if get_verbose():
            print('commands:')
            pprint(self.commands, indent=4)
        for pattern in patterns:
            if pattern in self.commands[action]:
                return self.commands[action][pattern]

    def enable(self):
        cmd = self.get_command(ENABLE)
        sudo_or_dryrun(cmd)

    def disable(self):
        cmd = self.get_command(DISABLE)
        sudo_or_dryrun(cmd)

    def restart(self):
        s = {'warn_only':True} if self.ignore_errors else {}
        restart_cmd = self.get_command(RESTART)
        if restart_cmd:
            with settings(**s):
                sudo_or_dryrun(restart_cmd)
        else:
            self.stop()
            self.start()

    def reload(self):
        s = {'warn_only':True} if self.ignore_errors else {}
        with settings(**s):
            cmd = self.get_command(RELOAD)
            sudo_or_dryrun(cmd)

    def start(self):
        s = {'warn_only':True} if self.ignore_errors else {}
        with settings(**s):
            cmd = self.get_command(START)
            sudo_or_dryrun(cmd)

    def stop(self, ignore_errors=True):
        s = {'warn_only': True} if ignore_errors else {}
        with settings(**s):
            cmd = self.get_command(STOP)
            sudo_or_dryrun(cmd)

    def status(self):
        with settings(warn_only=True):
            cmd = self.get_command(STATUS)
            return sudo_or_dryrun(cmd)

    @task
    def is_running(self):
        status = str(self.status() or '')
        status = re.sub(r'[\s\s]+', ' ', status)
        ret = 'is running' in status or 'start/running' in status or 'active (running)' in status
        if self.verbose:
            print('is_running.status:', status)
            print('is_running.ret:', ret)
        return ret

class ServiceSatchel(Satchel, Service):
    pass

class ContainerSatchel(Satchel):
    """
    Wraps functionality that doesn't need to track or deploy changes.
    """

    def record_manifest(self):
        return {}

    def configure(self):
        pass

def env_hosts_retriever(*args, **kwargs):
    data = {}
    if env.host_hostname:
        data[env.host_hostname] = {}
    return data.items()

def str_to_callable(s):
    s = (s or '').strip()
    if not s:
        return
    module_name = '.'.join(s.split('.')[:-1])
    func_name = s.split('.')[-1]
    return getattr(importlib.import_module(module_name), func_name)

def get_hosts_retriever(s=None):
    """
    Given the function name, looks up the method for dynamically retrieving host data.
    """
    s = s or env.hosts_retriever
#     #assert s, 'No hosts retriever specified.'
    if not s:
        return env_hosts_retriever
#     module_name = '.'.join(s.split('.')[:-1])
#     func_name = s.split('.')[-1]
#     retriever = getattr(importlib.import_module(module_name), func_name)
#     return retriever
    return str_to_callable(s) or env_hosts_retriever

def shellquote(s, singleline=True):
    if singleline:
        s = pipes.quote(s)
        s = repr(s)
        s = re.sub(r'^u*[\"\']+', '', s)
        s = re.sub(r'[\"\']+$', '', s)
        s = '"%s"' % s
    else:
        s = '{}'.format(pipes.quote(s))
    return s

def init_burlap_data_dir():
    d = env.burlap_data_dir
    print('env.plan_storage:', env.plan_storage)
    if env.plan_storage == 'local':
        if not os.path.isdir(env.burlap_data_dir):
            os.mkdir(d)
    else:
        if not d.startswith('/'):
            d = '/home/%s/%s' % (env.user, d)
        sudo_or_dryrun('mkdir -p "{directory}"; chown -R {user}:{user} {directory}'.format(user=env.user, directory=d))
    return d

def set_dryrun(dryrun):
    global _dryrun
    _dryrun = bool(int(dryrun or 0))
    if _dryrun:
        state.output.running = False
    else:
        state.output.running = True

def get_dryrun(dryrun=None):
    if dryrun is None or dryrun == '':
        return bool(int(_dryrun or 0))
    return bool(int(dryrun or 0))

def set_verbose(verbose):
    global _verbose
    _verbose = bool(int(verbose or 0))

def get_verbose(verbose=None):
    if verbose is None or verbose == '':
        return bool(int(_verbose or 0))
    return bool(int(verbose or 0))

def set_show(v):
    _show_command_output = bool(int(v))

def get_show():
    return _show_command_output

def render_command_prefix(is_local=False):
    extra = {}
    if env.key_filename:
        extra['key'] = env.key_filename
    extra_s = ''
    if extra:
        extra_s = json.dumps(extra)
    if is_local:
        s = '[%s@localhost]' % getpass.getuser()
    else:
        s = '[%s@%s%s]' % (env.user, env.host_string, extra_s)
    return s

def print_command(cmd):
    print('[%s@localhost] local: %s' % (getpass.getuser(), cmd))

def append_or_dryrun(*args, **kwargs):
    """
    Wrapper around Fabric's contrib.files.append() to give it a dryrun option.

    text filename

    http://docs.fabfile.org/en/0.9.1/api/contrib/files.html#fabric.contrib.files.append
    """
    from fabric.contrib.files import append

    dryrun = get_dryrun(kwargs.get('dryrun'))

    if 'dryrun' in kwargs:
        del kwargs['dryrun']

    use_sudo = kwargs.pop('use_sudo', False)

    text = args[0] if len(args) >= 1 else kwargs.pop('text')

    filename = args[1] if len(args) >= 2 else kwargs.pop('filename')

    if dryrun:
        text = text.replace('\n', '\\n')
        cmd = 'echo -e "%s" >> %s' % (text, filename)
        cmd_run = 'sudo' if use_sudo else 'run'
        if BURLAP_COMMAND_PREFIX:
            print('%s %s: %s' % (render_command_prefix(), cmd_run, cmd))
        else:
            print(cmd)
    else:
        append(filename=filename, text=text.replace(r'\n', '\n'), use_sudo=use_sudo, **kwargs)

def enable_attribute_or_dryrun(*args, **kwargs):
    """
    Similar to append() but ensures a line containing a key-value pair exists and is enabled.
    """
    dryrun = get_dryrun(kwargs.get('dryrun'))

    if 'dryrun' in kwargs:
        del kwargs['dryrun']

    use_sudo = kwargs.pop('use_sudo', False)
    run_cmd = sudo_or_dryrun if use_sudo else run_or_dryrun
    run_cmd_str = 'sudo' if use_sudo else 'run'

    key = args[0] if len(args) >= 1 else kwargs.pop('key')

    value = str(args[1] if len(args) >= 2 else kwargs.pop('value'))

    filename = args[2] if len(args) >= 3 else kwargs.pop('filename')

    comment_pattern = args[3] if len(args) >= 4 else kwargs.pop('comment_pattern', r'#\s*')

    equals_pattern = args[4] if len(args) >= 5 else kwargs.pop('equals_pattern', r'\s*=\s*')

    equals_literal = args[5] if len(args) >= 6 else kwargs.pop('equals_pattern', '=')

    context = dict(
        key=key,
        value=value,
        uncommented_literal='%s%s%s' % (key, equals_literal, value), # key=value
        uncommented_pattern='%s%s%s' % (key, equals_pattern, value), # key = value
        uncommented_pattern_partial='^%s%s[^\\n]*' % (key, equals_pattern), # key=
        commented_pattern='%s%s%s%s' % (comment_pattern, key, equals_pattern, value), # #key=value
        commented_pattern_partial='^%s%s%s[^\\n]*' % (comment_pattern, key, equals_pattern), # #key=
        filename=filename,
        backup=filename+'.bak',
        comment_pattern=comment_pattern,
        equals_pattern=equals_pattern,
    )

    cmds = [
        # Replace partial commented text with full un-commented text.
        'sed -i -r -e "s/{commented_pattern_partial}/{uncommented_literal}/g" {filename}'.format(**context),
        # Replace partial un-commented text with full un-commented text.
        'sed -i -r -e "s/{uncommented_pattern_partial}/{uncommented_literal}/g" {filename}'.format(**context),
        # Replace commented text with un-commented text.
        'sed -i -r -e "s/{commented_pattern}/{uncommented_literal}/g" {filename}'.format(**context),
        # If uncommented text still does not exist, append it.
        'grep -qE "{uncommented_pattern}" {filename} || echo "{uncommented_literal}" >> {filename}'.format(**context),
    ]

    if dryrun:
        for cmd in cmds:
            if BURLAP_COMMAND_PREFIX:
                print('%s %s: %s' % (render_command_prefix(), run_cmd_str, cmd))
            else:
                print(cmd)
    else:
        for cmd in cmds:
#             print('enable attr:', cmd)
            run_cmd(cmd)

def disable_attribute_or_dryrun(*args, **kwargs):
    """
    Comments-out a line containing an attribute.
    The inverse of enable_attribute_or_dryrun().
    """
    dryrun = get_dryrun(kwargs.get('dryrun'))

    if 'dryrun' in kwargs:
        del kwargs['dryrun']

    use_sudo = kwargs.pop('use_sudo', False)
    run_cmd = sudo_or_dryrun if use_sudo else run_or_dryrun
    run_cmd_str = 'sudo' if use_sudo else 'run'

    key = args[0] if len(args) >= 1 else kwargs.pop('key')

    filename = args[1] if len(args) >= 2 else kwargs.pop('filename')

    comment_pattern = args[2] if len(args) >= 3 else kwargs.pop('comment_pattern', r'#\s*')

    equals_pattern = args[3] if len(args) >= 4 else kwargs.pop('equals_pattern', r'\s*=\s*')

    equals_literal = args[4] if len(args) >= 5 else kwargs.pop('equals_pattern', '=')

    context = dict(
        key=key,
        uncommented_literal='%s%s' % (key, equals_literal), # key=value
        uncommented_pattern='%s%s' % (key, equals_pattern), # key = value
        uncommented_pattern_partial='^%s%s[^\\n]*' % (key, equals_pattern), # key=
        commented_pattern='%s%s%s' % (comment_pattern, key, equals_pattern), # #key=value
        commented_pattern_partial='^%s%s%s[^\\n]*' % (comment_pattern, key, equals_pattern), # #key=
        filename=filename,
        backup=filename+'.bak',
        comment_pattern=comment_pattern,
        equals_pattern=equals_pattern,
    )

    cmds = [
        # Replace partial un-commented text with full commented text.
        'sed -i -r -e "s/{uncommented_pattern_partial}//g" {filename}'.format(**context),
    ]

    if dryrun:
        for cmd in cmds:
            if BURLAP_COMMAND_PREFIX:
                print('%s %s: %s' % (render_command_prefix(), run_cmd_str, cmd))
            else:
                print(cmd)
    else:
        for cmd in cmds:
#             print('enable attr:', cmd)
            run_cmd(cmd)

def files_exists_or_dryrun(path, *args, **kwargs):
#     dryrun = get_dryrun(kwargs.get('dryrun'))
#     if dryrun:
#         use_sudo = kwargs.get('use_sudo', False)
#         cmd = '[ -d {path} ] || [ -f {path} ]'.format(path=path)
#         cmd_run = 'sudo' if use_sudo else 'run'
#         if BURLAP_COMMAND_PREFIX:
#             print('%s %s: %s' % (render_command_prefix(), cmd_run, cmd))
#         else:
#             print(cmd)
#         return False
#     else:
    from fabric.contrib.files import exists
    # Expand ~, since this isn't done automatically.
    if path and path.startswith('~'):
        path = '/home/%s/%s' % (env.user, path[1:])
    if env.host_string in LOCALHOSTS:
        return os.path.exists(path)
    return exists(path, *args, **kwargs)

def write_temp_file_or_dryrun(content, *args, **kwargs):
    """
    Writes the given content to a local temporary file.
    """
    dryrun = get_dryrun(kwargs.get('dryrun'))
    if dryrun:
        fd, tmp_fn = tempfile.mkstemp()
        os.remove(tmp_fn)
        cmd_run = 'local'
        cmd = 'cat <<EOT >> %s\n%s\nEOT' % (tmp_fn, content)
        if BURLAP_COMMAND_PREFIX:
            print('%s %s: %s' % (render_command_prefix(), cmd_run, cmd))
        else:
            print(cmd)
    else:
        fd, tmp_fn = tempfile.mkstemp()
        fout = open(tmp_fn, 'w')
        fout.write(content)
        fout.close()
    return tmp_fn

def sed_or_dryrun(*args, **kwargs):
    """
    Wrapper around Fabric's contrib.files.sed() to give it a dryrun option.

    http://docs.fabfile.org/en/0.9.1/api/contrib/files.html#fabric.contrib.files.sed
    """
    dryrun = get_dryrun(kwargs.get('dryrun'))
    if 'dryrun' in kwargs:
        del kwargs['dryrun']

    use_sudo = kwargs.get('use_sudo', False)

    if dryrun:
        context = dict(
            filename=args[0] if len(args) >= 1 else kwargs['filename'],
            before=args[1] if len(args) >= 2 else kwargs['before'],
            after=args[2] if len(args) >= 3 else kwargs['after'],
            backup=args[3] if len(args) >= 4 else kwargs.get('backup', '.bak'),
            limit=kwargs.get('limit', ''),
        )
        cmd = 'sed -i{backup} -r -e "/{limit}/ s/{before}/{after}/g {filename}"'.format(**context)
        cmd_run = 'sudo' if use_sudo else 'run'
        if BURLAP_COMMAND_PREFIX:
            print('%s %s: %s' % (render_command_prefix(), cmd_run, cmd))
        else:
            print(cmd)
    else:
        from fabric.contrib.files import sed
        sed(*args, **kwargs)

def local_or_dryrun(*args, **kwargs):
    dryrun = get_dryrun(kwargs.get('dryrun'))
    if 'dryrun' in kwargs:
        del kwargs['dryrun']

    assign_to = kwargs.pop('assign_to', None)
    if assign_to:
        cmd = args[0]
        cmd = '$%s=`%s`' % (assign_to, cmd)
        args = list(args)
        args[0] = cmd

    if dryrun:
        cmd = args[0]
        print('[%s@localhost] local: %s' % (getpass.getuser(), cmd))
    else:
        return local(*args, **kwargs)

def run_or_dryrun(*args, **kwargs):
    dryrun = get_dryrun(kwargs.get('dryrun'))
    if 'dryrun' in kwargs:
        del kwargs['dryrun']
    cmd = args[0] if args else ''
    assert cmd, 'No command specified.'
    if dryrun:
        if BURLAP_COMMAND_PREFIX:
            print('%s run: %s' % (render_command_prefix(), cmd))
        else:
            print(cmd)
    else:
        return _run(*args, **kwargs)


def begincap():
    """
    Prepares the output for Bash capture by clearing the line prefix.
    """
    global BURLAP_COMMAND_PREFIX, _tmp_BURLAP_COMMAND_PREFIX
    _tmp_BURLAP_COMMAND_PREFIX = BURLAP_COMMAND_PREFIX
    BURLAP_COMMAND_PREFIX = 0


def restorecap():
    """
    Resets the line prefix setting to whatever it was prior to calling begincap().
    """
    global BURLAP_COMMAND_PREFIX
    BURLAP_COMMAND_PREFIX = _tmp_BURLAP_COMMAND_PREFIX


def endcap():
    """
    Forcibly ends Bash capture by re-enabling the default line prefix.
    """
    global BURLAP_COMMAND_PREFIX
    BURLAP_COMMAND_PREFIX = 1


def escape_double_quotes_in_command(cmd):
    """
    Prefixes double-quotes with a backslash, so the command can be placed inside double-quotes for use in a Bash expression.
    """
    return re.sub(r'(?<!\\)"', '\\"', cmd)


def sudo_or_dryrun(*args, **kwargs):
    dryrun = get_dryrun(kwargs.get('dryrun'))
    user = kwargs.get('user')
    ignore_errors = int(kwargs.pop('ignore_errors', 0))
    if 'dryrun' in kwargs:
        del kwargs['dryrun']
    if dryrun:
        cmd = args[0]
        if BURLAP_COMMAND_PREFIX:
            if user:
                print('%s run: sudo -u %s bash -c "%s"' % (render_command_prefix(), user, escape_double_quotes_in_command(cmd)))
            else:
                print('%s run: sudo bash -c "%s"' % (render_command_prefix(), escape_double_quotes_in_command(cmd)))
        else:
            if user:
                print('sudo -u %s bash -c "%s"' % (user, escape_double_quotes_in_command(cmd)))
            else:
                print('sudo bash -c "%s"' % (escape_double_quotes_in_command(cmd),))
    else:
        if ignore_errors:
            with settings(warn_only=True):
                return _sudo(*args, **kwargs)
        else:
            return _sudo(*args, **kwargs)

def reboot_or_dryrun(*args, **kwargs):
    """
    An improved version of fabric.operations.reboot with better error handling.
    """
    from fabric.state import connections

    verbose = get_verbose()

    dryrun = get_dryrun(kwargs.get('dryrun'))

    # Use 'wait' as max total wait time
    kwargs.setdefault('wait', 120)
    wait = int(kwargs['wait'])

    command = kwargs.get('command', 'reboot')

    now = int(kwargs.get('now', 0))
    print('now:', now)
    if now:
        command += ' now'

    # Shorter timeout for a more granular cycle than the default.
    timeout = int(kwargs.get('timeout', 30))

    reconnect_hostname = kwargs.pop('new_hostname', env.host_string)

    if 'dryrun' in kwargs:
        del kwargs['dryrun']

    if dryrun:
        print('%s sudo: %s' % (render_command_prefix(), command))
    else:
        if is_local():
            if six.moves.input('reboot localhost now? ').strip()[0].lower() != 'y':
                return

        attempts = int(round(float(wait) / float(timeout)))
        # Don't bleed settings, since this is supposed to be self-contained.
        # User adaptations will probably want to drop the "with settings()" and
        # just have globally set timeout/attempts values.
        with settings(warn_only=True):
            _sudo(command)

        env.host_string = reconnect_hostname
        success = False
        for attempt in six.moves.range(attempts):

            # Try to make sure we don't slip in before pre-reboot lockdown
            if verbose:
                print('Waiting for %s seconds, wait %i of %i' % (timeout, attempt+1, attempts))
            time.sleep(timeout)

            # This is actually an internal-ish API call, but users can simply drop
            # it in real fabfile use -- the next run/sudo/put/get/etc call will
            # automatically trigger a reconnect.
            # We use it here to force the reconnect while this function is still in
            # control and has the above timeout settings enabled.
            try:
                if verbose:
                    print('Reconnecting to:', env.host_string)
                # This will fail until the network interface comes back up.
                connections.connect(env.host_string)
                # This will also fail until SSH is running again.
                with settings(timeout=timeout):
                    _run('echo hello')
                success = True
                break
            except Exception as e:
                print('Exception:', e)

        if not success:
            raise Exception('Reboot failed or took longer than %s seconds.' % wait)

# def get_or_dryrun(*args, **kwargs):
#     dryrun = get_dryrun(kwargs.get('dryrun'))
#     use_sudo = kwargs.get('use_sudo', False)
#     real_remote_path = None
#     if 'dryrun' in kwargs:
#         del kwargs['dryrun']
#     if dryrun:
#         local_path = kwargs['local_path']
#         remote_path = kwargs.get('remote_path', None)
#
#         if not local_path:
#             _, local_path = tempfile.mkstemp()
#
#         if not local_path.startswith('/') and not local_path.startswith('~'):
#             local_path = '/tmp/' + local_path
#
#         if use_sudo:
#             real_local_path = local_path
#             _, local_path = tempfile.mkstemp()
#
#         if real_local_path is None:
#             real_local_path = local_path
#
#         if env.host_string in LOCALHOSTS:
#             cmd = 'rsync --progress --verbose %s %s' % (remote_path, local_path)
#             print('%s get: %s' % (render_command_prefix(is_local=True), cmd))
#             env.get_local_path = local_path
#         else:
#             cmd = 'rsync --progress --verbose %s %s@%s:%s' % (local_path, env.user, env.host_string, local_path)
#             env.get_local_path = local_path
#             print('%s get: %s' % (render_command_prefix(is_local=True), cmd))
#
#         if real_local_path and use_sudo:
#             sudo_or_dryrun('mv %s %s' % (local_path, real_local_path))
#             env.get_local_path = real_local_path
#
#         return [real_local_path]
#     else:
#         return _get(**kwargs)

def rsync_or_dryrun(**kwargs):
    dryrun = get_dryrun(kwargs.get('dryrun'))
    use_sudo = kwargs.get('use_sudo', False)
    local_path = kwargs.pop('local_path')
    remote_path = kwargs.pop('remote_path')
    #cmd = 'rsync --progress --verbose %s %s@%s:%s' % (local_path, env.user, env.host_string, remote_path)
    cmd = 'rsync -avz --progress --rsh "ssh -i %s" "%s" %s@%s:"%s"' % (env.key_filename, local_path, env.user, env.host_string, remote_path)
    if dryrun:
        print(cmd)
    else:
        _local(cmd, **kwargs)

def put_or_dryrun(*args, **kwargs):
    dryrun = get_dryrun(kwargs.get('dryrun'))
    use_sudo = kwargs.get('use_sudo', False)
    real_remote_path = None
    if 'dryrun' in kwargs:
        del kwargs['dryrun']
    if dryrun:
        local_path = kwargs['local_path']
        remote_path = kwargs.get('remote_path', None)

        if not remote_path:
            _, remote_path = tempfile.mkstemp()

        if not env.is_local and not remote_path.startswith('/') and not remote_path.startswith('~'):
            remote_path = '/tmp/' + remote_path

        if use_sudo:
            real_remote_path = remote_path
            _, remote_path = tempfile.mkstemp()

        if real_remote_path is None:
            real_remote_path = remote_path

        if env.host_string in LOCALHOSTS:
            cmd = 'rsync --progress --verbose %s %s' % (local_path, remote_path)
            print('%s put: %s' % (render_command_prefix(is_local=True), cmd))
            env.put_remote_path = local_path
        else:
            cmd = 'rsync --progress --verbose %s %s@%s:%s' % (local_path, env.user, env.host_string, remote_path)
            env.put_remote_path = remote_path
            print('%s put: %s' % (render_command_prefix(is_local=True), cmd))

        if real_remote_path and use_sudo:
            sudo_or_dryrun('mv %s %s' % (remote_path, real_remote_path))
            env.put_remote_path = real_remote_path

        return [real_remote_path]

    if env.host_string in LOCALHOSTS or env.is_local:
        if use_sudo:
            sudo_or_dryrun('cp {local_path} {remote_path}'.format(**kwargs))
        else:
            local_or_dryrun('cp {local_path} {remote_path}'.format(**kwargs))
        env.put_remote_path = kwargs.get('remote_path')

    return _put(**kwargs)


def get_or_dryrun(**kwargs):
    dryrun = get_dryrun(kwargs.get('dryrun'))
    use_sudo = kwargs.get('use_sudo', False)
    if 'dryrun' in kwargs:
        del kwargs['dryrun']
    if dryrun:
        local_path = kwargs['local_path']
        remote_path = kwargs.get('remote_path', None)
        if not local_path:
            local_path = tempfile.mktemp()
        if not local_path.startswith('/'):
            local_path = '/tmp/' + local_path
        cmd = ('sudo ' if use_sudo else '')+'rsync --progress --verbose %s@%s:%s %s' % (env.user, env.host_string, remote_path, local_path)
        print('[localhost] get: %s' % (cmd,))
        env.get_local_path = local_path
    else:
        return _get(**kwargs)


def _get(*args, **kwargs):
    ret = __get(*args, **kwargs)
    env.get_local_path = ret
    return ret


def pretty_bytes(bytes): # pylint: disable=redefined-builtin
    """
    Scales a byte count to the largest scale with a small whole number
    that's easier to read.
    Returns a tuple of the format (scaled_float, unit_string).
    """
    if not bytes:
        return bytes, 'bytes'
    sign = bytes/float(bytes)
    bytes = abs(bytes)
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            #return "%3.1f %s" % (bytes, x)
            return sign*bytes, x
        bytes /= 1024.0


def get_component_settings(prefixes=None):
    """
    Returns a subset of the env dictionary containing
    only those keys with the name prefix.
    """
    prefixes = prefixes or []
    assert isinstance(prefixes, (tuple, list)), 'Prefixes must be a sequence type, not %s.' % type(prefixes)
    data = {}
    for name in prefixes:
        name = name.lower().strip()
        for k in sorted(env):
            if k.startswith('%s_' % name):
                new_k = k[len(name)+1:]
                data[new_k] = env[k]
    return data


def get_last_modified_timestamp(path, ignore=None):
    """
    Recursively finds the most recent timestamp in the given directory.
    """
    ignore = ignore or []
    if not isinstance(path, six.string_types):
        return
    ignore_str = ''
    if ignore:
        assert isinstance(ignore, (tuple, list))
        ignore_str = ' '.join("! -name '%s'" % _ for _ in ignore)
    cmd = 'find "'+path+'" ' + ignore_str + ' -type f -printf "%T@ %p\n" | sort -n | tail -1 | cut -f 1 -d " "'
         #'find '+path+' -type f -printf "%T@ %p\n" | sort -n | tail -1 | cut -d " " -f1
    ret = subprocess.check_output(cmd, shell=True)
    # Note, we round now to avoid rounding errors later on where some formatters
    # use different decimal contexts.
    try:
        ret = round(float(ret), 2)
    except ValueError:
        return
    return ret


def check_settings_for_differences(old, new, as_bool=False, as_tri=False):
    """
    Returns a subset of the env dictionary keys that differ,
    either being added, deleted or changed between old and new.
    """

    assert not as_bool or not as_tri

    old = old or {}
    new = new or {}

    changes = set(k for k in set(new.iterkeys()).intersection(old.iterkeys()) if new[k] != old[k])
    if changes and as_bool:
        return True

    added_keys = set(new.iterkeys()).difference(old.iterkeys())
    if added_keys and as_bool:
        return True
    if not as_tri:
        changes.update(added_keys)

    deled_keys = set(old.iterkeys()).difference(new.iterkeys())
    if deled_keys and as_bool:
        return True
    if as_bool:
        return False
    if not as_tri:
        changes.update(deled_keys)

    if as_tri:
        return added_keys, changes, deled_keys

    return changes


def get_subpackages(module):
    dr = os.path.dirname(module.__file__)
    def is_package(d):
        d = os.path.join(dr, d)
        return os.path.isdir(d) and glob.glob(os.path.join(d, '__init__.py*'))
    return filter(is_package, os.listdir(dr))


def get_submodules(module):
    dr = os.path.dirname(module.__file__)
    def is_module(d):
        d = os.path.join(dr, d)
        return os.path.isfile(d) and glob.glob(os.path.join(d, '*.py*'))
    return filter(is_module, os.listdir(dr))


def iter_apps():
    sys.path.insert(0, os.getcwd())
    arch = importlib.import_module('arch')
    settings = importlib.import_module('arch.settings')
    INSTALLED_APPS = set(settings.INSTALLED_APPS)
    for sub_name in get_subpackages(arch):
        if sub_name in INSTALLED_APPS:
            yield sub_name


def get_app_package(name):
    sys.path.insert(0, os.getcwd())
    arch = importlib.import_module('arch')
    settings = importlib.import_module('arch.settings')
    INSTALLED_APPS = set(settings.INSTALLED_APPS)
    assert name in INSTALLED_APPS, 'Unknown or uninstalled app: %s' % (name,)
    return importlib.import_module('arch.%s' % name)


def to_dict(obj):
    if isinstance(obj, (tuple, list)):
        return [to_dict(_) for _ in obj]
    if isinstance(obj, dict):
        return dict((to_dict(k), to_dict(v)) for k, v in six.iteritems(obj))
    if isinstance(obj, (int, bool, float, six.string_types)):
        return obj
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    raise Exception('Unknown type: %s %s' % (obj, type(obj)))

class QueuedCommand:
    """
    Represents a fabric command that is pending execution.
    """

    def __init__(self, name, args=None, kwargs=None, pre=None, post=None):
        self.name = name
        self.args = args or []
        self.kwargs = kwargs or {}

        pre = pre or []
        post = post or []

        # Used for ordering commands.
        self.pre = pre # commands that should come before this command
        assert isinstance(self.pre, (tuple, list)), 'Pre must be a list type.'
        self.post = post # commands that should come after this command
        assert isinstance(self.post, (tuple, list)), 'Post must be a list type.'

    @property
    def cn(self):
        """
        Returns the component name, if given in the name
        as "<component_name>.method".
        """
        parts = self.name.split('.')
        if len(parts) >= 2:
            return parts[0]

    def __repr__(self):
        kwargs = list(map(str, self.args))
        for k, v in six.iteritems(self.kwargs):
            if isinstance(v, bool):
                kwargs.append('%s=%i' % (k, int(v)))
            elif isinstance(v, six.string_types) and '=' in v:
                # Escape equals sign character in parameter values.
                kwargs.append('%s="%s"' % (k, v.replace('=', r'\=')))
            else:
                kwargs.append('%s=%s' % (k, v))
        params = (self.name, ','.join(kwargs))
        if params[1]:
            return ('%s:%s' % params).strip()
        return (params[0]).strip()

    def __cmp__(self, other):
        """
        Return negative if x<y, zero if x==y, positive if x>y.
        """
        if not isinstance(self, type(other)):
            return NotImplemented

        x_cn = self.cn
        x_name = self.name
        x_pre = self.pre
        x_post = self.post

        y_cn = other.cn
        y_name = other.name
        y_pre = other.pre
        y_post = other.post

        if y_cn in x_pre or y_name in x_pre:
            # Other should come first.
            return +1
        if y_cn in x_post or y_name in x_post:
            # Other should come last.
            return -1
        if x_cn in y_pre or x_name in y_pre:
            # We should come first.
            return -1
        if x_cn in y_post or x_name in y_post:
            # We should come last.
            return -1
        return 0
        #return cmp(hash(self), hash(other))

    def __hash__(self):
        return hash((self.name, tuple(self.args), tuple(self.kwargs.items())))

    def __call__(self):
        raise NotImplementedError


def get_template_dirs():
    # This must be an iterator so we can easily update the env variables used.
    verbose = get_verbose()
    if verbose:
        print('get_template_dirs.env.ROLES_DIR:', env.ROLES_DIR)
        print('get_template_dirs.os.getcwd():', os.getcwd())
    paths = (
        (env.ROLES_DIR, env[ROLE], 'templates'),
        (env.ROLES_DIR, env[ROLE]),
        (env.ROLES_DIR, '..', 'templates', env[ROLE]),
        (env.ROLES_DIR, '..', 'satchels', 'templates'),
        (env.ROLES_DIR, ALL, 'templates'),
        (env.ROLES_DIR, ALL),
        (env.ROLES_DIR, '..', 'templates', ALL),
        (env.ROLES_DIR, '..', 'templates'),
        (os.path.dirname(__file__), 'templates'),
    )
    for path in paths:
        if None in path:
            continue
        yield os.path.join(*path)
    #env.template_dirs = get_template_dirs()

#env.template_dirs = get_template_dirs()

def save_env():
    env_default = {}
    for k, v in six.iteritems(env):
        if k.startswith('_'):
            continue
        elif isinstance(v, (types.GeneratorType, types.ModuleType)):
            continue
        env_default[k] = copy.deepcopy(v)
    return env_default

try:
    from django.conf import settings as _settings
    _settings.configure(TEMPLATE_DIRS=get_template_dirs())
except (ImportError, RuntimeError):
    warnings.warn('Unable to import Django settings.', ImportWarning)

def _put(**kwargs):
    local_path = kwargs['local_path']
    fd, fn = tempfile.mkstemp()
    if not is_local():
        os.remove(fn)
    #kwargs['remote_path'] = kwargs.get('remote_path', '/tmp/%s' % os.path.split(local_path)[-1])
    kwargs['remote_path'] = kwargs.get('remote_path', fn)
    env.put_remote_path = kwargs['remote_path']
    return __put(**kwargs)

def get_rc(k):
    if '_rc' in env:
        return env._rc.get(env[ROLE], type(env)()).get(k)

def set_rc(k, v):
    if '_rc' not in env:
        env._rc = type(env)()
    env._rc.setdefault(env[ROLE], type(env)())
    env._rc[env[ROLE]][k] = v

def get_packager():
    """
    Returns the packager detected on the remote system.
    """

    # TODO: remove once fabric stops using contextlib.nested.
    # https://github.com/fabric/fabric/issues/1364
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    common_packager = get_rc('common_packager')
    if common_packager:
        return common_packager
    #TODO:cache result by current env.host_string so we can handle multiple hosts with different OSes
    with settings(warn_only=True):
        with hide('running', 'stdout', 'stderr', 'warnings'):
            ret = _run('cat /etc/fedora-release')
            if ret.succeeded:
                common_packager = YUM
            else:
                ret = _run('cat /etc/lsb-release')
                if ret.succeeded:
                    common_packager = APT
                else:
                    for pn in PACKAGERS:
                        ret = _run('which %s' % pn)
                        if ret.succeeded:
                            common_packager = pn
                            break
    if not common_packager:
        raise Exception('Unable to determine packager.')
    set_rc('common_packager', common_packager)
    return common_packager

def _run_or_local(cmd):
    if env.host_string in LOCALHOSTS:
        ret = _local(cmd, capture=True)
    else:
        ret = _run(cmd)
    return ret

def get_os_version():
    """
    Returns a named tuple describing the operating system on the remote host.
    """

    # TODO: remove once fabric stops using contextlib.nested.
    # https://github.com/fabric/fabric/issues/1364
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    common_os_version = get_rc('common_os_version')
    if common_os_version:
        return common_os_version
    with settings(warn_only=True):
        with hide('running', 'stdout', 'stderr', 'warnings'):

            ret = _run_or_local('cat /etc/lsb-release')
            if ret.succeeded:
                return OS(
                    type=LINUX,
                    distro=UBUNTU,
                    release=re.findall(r'DISTRIB_RELEASE=([0-9\.]+)', ret)[0])

            ret = _run_or_local('cat /etc/debian_version')
            if ret.succeeded:
                return OS(
                    type=LINUX,
                    distro=DEBIAN,
                    release=re.findall(r'([0-9\.]+)', ret)[0])

            ret = _run_or_local('cat /etc/fedora-release')
            if ret.succeeded:
                return OS(
                    type=LINUX,
                    distro=FEDORA,
                    release=re.findall(r'release ([0-9]+)', ret)[0])

            raise Exception('Unable to determine OS version.')

def find_template(template):
    verbose = get_verbose()
    final_fqfn = None
    for path in get_template_dirs():
        if verbose:
            print('Checking "%s" for "%s"...' % (path, template))
        fqfn = os.path.abspath(os.path.join(path, template))
        if os.path.isfile(fqfn):
            if verbose:
                print('Using template: %s' % (fqfn,))
            final_fqfn = fqfn
            break

    if not final_fqfn:
        raise IOError('Template not found: %s' % template)

    return final_fqfn

def get_template_contents(template):
    final_fqfn = find_template(template)
    return open(final_fqfn).read()

def render_to_string(template, extra=None):
    """
    Renders the given template to a string.
    """
    from jinja2 import Template
    extra = extra or {}
    final_fqfn = find_template(template)
    assert final_fqfn, 'Template not found: %s' % template
    template_content = open(final_fqfn, 'r').read()
    t = Template(template_content)
    if extra:
        context = env.copy()
        context.update(extra)
    else:
        context = env
    rendered_content = t.render(**context)
    rendered_content = rendered_content.replace('&quot;', '"')
    return rendered_content

def render_to_file(template, fn=None, extra=None, **kwargs):
    """
    Returns a template to a local file.
    If no filename given, a temporary filename will be generated and returned.
    """
    import tempfile
    dryrun = get_dryrun(kwargs.get('dryrun'))
    append_newline = kwargs.pop('append_newline', True)
    style = kwargs.pop('style', 'cat') # |echo
    formatter = kwargs.pop('formatter', None)
    content = render_to_string(template, extra=extra)
    if append_newline and not content.endswith('\n'):
        content += '\n'

    if formatter and callable(formatter):
        content = formatter(content)

    if dryrun:
        if not fn:
            fd, fn = tempfile.mkstemp()
            fout = os.fdopen(fd, 'wt')
            fout.close()
    else:
        if fn:
            fout = open(fn, 'w')
        else:
            fd, fn = tempfile.mkstemp()
            fout = os.fdopen(fd, 'wt')
        fout.write(content)
        fout.close()
    assert fn

    if style == 'cat':
        cmd = 'cat <<EOF > %s\n%s\nEOF' % (fn, content)
    elif style == 'echo':
        cmd = 'echo -e %s > %s' % (shellquote(content), fn)
    else:
        raise NotImplementedError

    if BURLAP_COMMAND_PREFIX:
        print('%s run: %s' % (render_command_prefix(), cmd))
    else:
        print(cmd)

    return fn

def install_config(local_path=None, remote_path=None, render=True, extra=None, formatter=None):
    """
    Returns a template to a remote file.
    If no filename given, a temporary filename will be generated and returned.
    """
    local_path = find_template(local_path)
    if render:
        extra = extra or {}
        local_path = render_to_file(template=local_path, extra=extra, formatter=formatter)
    put_or_dryrun(local_path=local_path, remote_path=remote_path, use_sudo=True)

def install_script(*args, **kwargs):
    install_config(*args, **kwargs)
    sudo_or_dryrun('chmod +x %s' % env.put_remote_path)

def write_to_file(content, fn=None, **kwargs):

    dryrun = get_dryrun(kwargs.get('dryrun'))

    if not fn:
        fd, fn = tempfile.mkstemp()

    if dryrun:
        cmd = 'echo -e %s > %s' % (shellquote(content), fn)
        if BURLAP_COMMAND_PREFIX:
            print('%s local: %s' % (render_command_prefix(is_local=True), cmd))
        else:
            print(cmd)
    else:
        if fn:
            fout = open(fn, 'w')
        else:
            fout = os.fdopen(fd, 'wt')
        fout.write(content)
        fout.close()
    return fn

def upload_content(content, fn, **kwargs):
    tmp_fn = write_to_file(content=content, **kwargs)
    use_sudo = kwargs.pop('use_sudo', env.host_string not in LOCALHOSTS)
    put_or_dryrun(local_path=tmp_fn, remote_path=fn, use_sudo=use_sudo)

def set_site(site):
    if site is None:
        return
    env[SITE] = os.environ[SITE] = site

def set_role(role):
    if role is None:
        return
    env[ROLE] = os.environ[ROLE] = role


class RoleLoader():
    """
    A context manager that temporarily loads a role and site configuration.
    """

    def __init__(self, role, site=None):
        import burlap
        self.role0 = env[ROLE]
        self.role = role
        self.role_loader = getattr(burlap, 'role_%s' % role)
        self.site0 = env[SITE]
        self.site = site
        self.iter = None

    def __enter__(self):
        # Populate env.
        self.iter = iter_sites(site=self.site, role_loader=partial(self.role_loader, site=self.site))
        ret = next(self.iter)

    def __exit__(self, *args):
        # Cleanup env.
        try:
            while 1:
                ret = next(self.iter)
        except StopIteration:
            pass
        env[ROLE] = self.role0
        env[SITE] = self.site0


def iter_sites(sites=None, site=None, renderer=None, setter=None, no_secure=False, verbose=None, role_loader=None):
    """
    Iterates over sites, safely setting environment variables for each site.
    """
    if verbose is None:
        verbose = get_verbose()

    hostname = get_current_hostname()

    target_sites = env.available_sites_by_host.get(hostname, None)

    if sites is None:
        site = site or env.SITE or ALL
        if site == ALL:
            sites = list(six.iteritems(env.sites))
        else:
            sys.stderr.flush()
            sites = [(site, env.sites.get(site))]

    renderer = renderer #or render_remote_paths
    env_default = save_env()
    if callable(role_loader):
        role_loader()
    env_default_role = save_env()
    for _site, site_data in sorted(sites):
        if no_secure and _site.endswith('_secure'):
            continue

        # Only load site configurations that are allowed for this host.
        if target_sites is None:
            pass
        else:
            assert isinstance(target_sites, (tuple, list))
            if _site not in target_sites:
                if verbose:
                    print('Skipping site %s because not in among target sites.' % _site)
                continue

        env.update(env_default_role)
        env.update(env.sites.get(_site, {}))
        env.SITE = _site
        if callable(renderer):
            renderer()
        if setter:
            setter(_site)
        yield _site, site_data

    # Revert modified keys.
    env.update(env_default)

    # Remove keys that were added, not simply updated.
    added_keys = set(env).difference(env_default)
    for key in added_keys:
        # Don't remove internally maintained variables, because these are used to cache hostnames
        # used by iter_sites().
        if key.startswith('_'):
            continue
        del env[key]

def pc(*args):
    """
    Print comment.
    """
    print('echo "%s"' % ' '.join(map(str, args)))

def get_current_hostname():
    key = '_ip_to_hostname'
    if key not in env:
        env[key] = {}
#    import importlib
#
#    retriever = None
#    if env.hosts_retriever:
#        # Dynamically retrieve hosts.
#        module_name = '.'.join(env.hosts_retriever.split('.')[:-1])
#        func_name = env.hosts_retriever.split('.')[-1]
#        retriever = getattr(importlib.import_module(module_name), func_name)
#
#    # Load host translator.
#    translator = None
#    if hostname:
#        # Filter hosts list by a specific host name.
#        module_name = '.'.join(env.hostname_translator.split('.')[:-1])
#        func_name = env.hostname_translator.split('.')[-1]
#        translator = getattr(importlib.import_module(module_name), func_name)
    #ret = run_or_dryrun('hostname')#)

    if not env.host_string:
        env.host_string = LOCALHOST_NAME

    if env.host_string not in env[key]:
        with hide('running', 'stdout', 'stderr', 'warnings'):
            if env.host_string in LOCALHOSTS:
                ret = _local('hostname', capture=True)
            else:
                ret = _run('hostname')
        env[key][env.host_string] = str(ret).strip()

    return env[key][env.host_string]

#http://stackoverflow.com/questions/11557241/python-sorting-a-dependency-list
def topological_sort(source):
    """perform topo sort on elements.

    :arg source: list of ``(name, [list of dependancies])`` pairs
    :returns: list of names, with dependancies listed first
    """
    if isinstance(source, dict):
        source = source.items()
    pending = sorted([(name, set(deps)) for name, deps in source]) # copy deps so we can modify set in-place
    emitted = []
    while pending:
        next_pending = []
        next_emitted = []
        for entry in pending:
            name, deps = entry
            deps.difference_update(emitted) # remove deps we emitted last pass
            if deps: # still has deps? recheck during next pass
                next_pending.append(entry)
            else: # no more deps? time to emit
                yield name
                emitted.append(name) # <-- not required, but helps preserve original ordering
                next_emitted.append(name) # remember what we emitted for difference_update() in next pass
        if not next_emitted: # all entries have unmet deps, one of two things is wrong...
            raise ValueError("cyclic or missing dependancy detected: %r" % (next_pending,))
        pending = next_pending
        emitted = next_emitted

def represent_ordereddict(dumper, data):
    value = []

    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        value.append((node_key, node_value))

    return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', value)

yaml.add_representer(OrderedDict, represent_ordereddict)

#TODO:make thread/process safe with lockfile?

shelf = Shelf()

def get_host_ip(hostname):
    #TODO:use generic host retriever?
    from burlap.vm import list_instances
    data = list_instances(show=0, verbose=0)
    for key, attrs in six.iteritems(data):
#         print('key:',key,attrs)
        if key == hostname:
            return attrs.get('ip')

def only_hostname(s):
    """
    Given an SSH target, returns only the hostname.

    e.g. only_hostname('user@mydomain:port') == 'mydomain'
    """
    return s.split('@')[-1].split(':')[0].strip()

def get_hosts_for_site(site=None):
    """
    Returns a list of hosts that have been configured to support the given site.
    """
    site = site or env.SITE
    hosts = set()
    for hostname, _sites in six.iteritems(env.available_sites_by_host):
#         print('checking hostname:',hostname, _sites)
        for _site in _sites:
            if _site == site:
#                 print( '_site:',_site)
                host_ip = get_host_ip(hostname)
#                 print( 'host_ip:',host_ip)
                if host_ip:
                    hosts.add(host_ip)
                    break
    return list(hosts)

def getoutput(cmd):
    return subprocess.check_output(cmd, shell=True)
#     process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
#     out, err = process.communicate()
#     return out
