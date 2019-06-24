# encoding: utf8
"""Load and validate a python module received as a filename.

"""
import os
import re
import glob
import json
import inspect
import textwrap
import importlib
import itertools
from functools import partial
from collections import defaultdict

import clyngor
from biseau import utils
from biseau import script as script_functions
from biseau.script import Script, Module


DEFAULT_DOC = 'NO SCRIPT DOC PROVIDED.\nFix this by writing a module documentation inside script definition.'
RETURNS_TYPES = {iter, str}
OPTIONS_TYPES = {int, float, bool, str, open, (open, 'r'), (open, 'w')}
TYPE_DEFAULT = {int: 0, float: 0., bool: False, str: '', open: None}
REGEX_OPTION_DESC = re.compile(r'([a-zA-Z0-9_]+)\s*--\s*(.+)$')


class ScriptError(ValueError):
    def __init__(self, script, message):
        pass

    def __str__(self):
        return self.args[1]


def gen_files_in_dir(dirname:str, extensions:[str]=('py', 'lp', 'json'),
                       filter_prefixes:[str]='_') -> (str, str):
    "Yield candidate scripts in given dir, based on file extension"
    yield from (
        fname
        for fname in map(os.path.basename, glob.glob('{}/*.{{{}}}'.format(dirname, ','.join(extensions))))
        if not filter_prefixes or (filer_prefixes and not fname.startswith(filter_prefixes))
    )


def build_scripts_from_dir(dirname:str='scripts', options:dict={}) -> [Script]:
    "Yield all scripts found in given directory (not recursive)"
    for file in gen_files_in_dir(dirname):
        yield from build_scripts_from_file(file, options)

def build_scripts_from_file(fname:str, options:dict={}) -> [Script]:
    "Yield all scripts found in given file (note that only JSON files can define multiple scripts)"
    name, ext = os.path.splitext(fname)
    if ext == '.json':
        yield from build_scripts_from_json_file(fname)
    elif ext == '.py':
        try:
            script = build_python_script_from_name(name)
            yield script
        except ScriptError as err:
            print('SCRIPT ERROR:', str(err))
    elif ext == '.lp':
        yield build_asp_script_from_name(fname)
    elif fname.upper().startswith('ASP'):
        if isinstance(options, (list, tuple, str)):
            yield from build_scripts_from_asp_code(options)
        else:
            print(f"Unknow type for ASP code: {type(options)}")
    else:
        print(f"WARNING file '{fname}' was not recognized")


def merge_scripts_lists(*scripts_lists:iter) -> iter:
    """Yield scripts, ordered according to their dependancies"""
    yield from sort_scripts_per_dependancies(itertools.chain.from_iterable(scripts_lists))


def sort_scripts_per_dependancies(scripts:iter) -> iter:
    """Topological sort of scripts based on their inputs/outputs.

    Do not handle scripts interdependancies.

    """
    scripts = tuple(scripts)
    inputs = {script: frozenset(script.inputs()) for script in scripts}
    outputs = {script: frozenset(script.outputs()) for script in scripts}
    yield from topological_sort_by_io(inputs, outputs)


def topological_sort_by_io(inputs:dict, outputs:dict) -> iter:
    """Yield keys of inputs and outputs so that a value yielded after another
    is either in need of the previous's outputs, or unrelated.

    inputs -- mapping {value: {input}}
    outputs -- mapping {value: {output}}

    """
    # decide {pred: {succs}} for scripts
    topology = defaultdict(set)
    for script, input in inputs.items():
        topology[script]  # just ensure there is one
        for maybe_pred, output in outputs.items():
            if input & output or (input and '*/*' in output):
                topology[maybe_pred].add(script)
    successors = frozenset(itertools.chain.from_iterable(topology.values()))
    sources = {script for script in topology if script not in successors}
    # compute source, and decide a path
    prev_len = None
    while topology:  # while catch cycles
        while len(topology) != prev_len:
            prev_len = len(topology)
            yield from sources
            topology = {script: {succ for succ in succs if succ not in sources}
                        for script, succs in topology.items()
                        if script not in sources}
            successors = frozenset(itertools.chain.from_iterable(topology.values()))
            sources = {script for script in topology if script not in successors}
        if topology:  # there is at least one cycle
            # take a predecessor, say it is a source
            forced_source = next(iter(topology.keys()))
            sources = {forced_source}
            prev_len = None


def build_python_script_from_name(module_name) -> Script:
    path = module_name.replace('/', '.')
    import_as_module = True
    try:
        module = importlib.import_module(path)
    except TypeError:
        import_as_module = False

    if import_as_module:
        # Reload needed because the module itself is
        #  modified by build_script_from_module
        module = importlib.reload(module)
        return build_script_from_module(module)
    else:  # just load it savagely
        # module_name is not importable directly
        return build_script_from_json({'python file': module_name + '.py'})

def build_python_script_from_name(module_name) -> Script:
    "Replace the previous implementation. Limited, but we don't have to manage python modules as specific objects"
    return build_script_from_json({'python file': module_name + '.py'})


def build_asp_script_from_name(fname:str) -> str:
    with open(fname) as fd:
        asp_code = fd.read()
    name = os.path.splitext(os.path.basename(fname))[0]
    name.replace('_', ' ')
    with open(fname) as fd:
        description = []
        for line in fd:
            if line.startswith('% '):
                description.append(line[2:])
            else: break
    description = '\n'.join(description)
    # reuse the json interface
    return build_script_from_json({
        'name': name,
        'ASP': asp_code,
        'description': description,
        'inputs': [],
        'outputs': [],  # TODO: search for #show's in the file
    })


def build_scripts_from_json_file(fname:str) -> [Script]:
    """Yield Script instances found in given file in JSON format"""
    with open(fname) as fd:
        data = json.load(fd)
    if isinstance(data, list):  # multiple scripts
        for payload in data:
            yield build_script_from_json(payload)
    elif isinstance(data, dict):  # only one
        yield build_script_from_json(data)
    else:
        raise ScriptError(fname, "Given json file {} is not correctly formatted. "
                          "First object should be a list or a dict, not a {}"
                          "".format(fname, type(data)))


def build_scripts_from_asp_code(data:str or list) -> [Script]:
    """Yield one Script instance initialized with given source code"""
    if isinstance(data, (tuple, list)):  # multiple scripts
        for source in data:
            yield from build_scripts_from_asp_code(source)
    elif isinstance(data, str):  # only one
        yield build_script_from_json({
            'name': 'inline ASP code',
            'ASP': data,
            'language': 'asp',
            'description': 'inline ASP code',
            'inputs': [],
            'outputs': [],  # TODO: search for #show's in the file
        })
    else:
        raise ScriptError(data, f"Given ASP source of type {type(data)} can't be handled.")


def build_script_from_json(module_def:dict) -> Script:
    """From given JSON build a Script instance"""
    module = Module()

    # I/O
    module.INPUTS = frozenset(module_def.get('inputs', ()))
    module.OUTPUTS = frozenset(module_def.get('outputs', ()))

    # Fields
    module.NAME = module_def.get('name', 'unamed script')
    if 'tags' in module_def: module.TAGS = frozenset(module_def['tags'])
    module.__doc__ = module_def.get('description', DEFAULT_DOC)

    # building the run_on function
    if 'ASP file' in module_def:
        module.language = 'asp file'
        module.source_code = module_def['ASP file']
    elif 'ASP' in module_def:
        module.language = 'asp'
        module.source_code = module_def['ASP']
    elif 'python file' in module_def:
        module.language = 'python file'
        module.source_code = module_def['python file']
    elif 'python' in module_def:
        module.language = 'python'
        module.source_code = module_def['python']
    else:
        raise ValueError(f"JSON script {module.NAME} do not have any code field ('ASP' "
                         "or 'ASP file' for instance). If this script was "
                         "generated with Biseau, it's possible that you're "
                         "using an older version than the script creator."
                         "")
    return build_script_from_module(module)


def build_script_from_module(module, *, defaults:dict={}) -> Script or ScriptError:
    """Low level function. Expect module to be a python module, or a namespace
    emulating one.

    Will try hard to invalidate given module. If it seems valid, return
    a Script instance describing and referencing the module.

    defaults -- mapping from (name, tags, erase_context) to a
                default value to use if the module does not provide it.

    """
    if not hasattr(module, '__doc__'):
        bad_script_error(module, "Docstring (description) is missing")


    if hasattr(module, 'run_on'):
        run_on_func = module.run_on
        args = inspect.getfullargspec(module.run_on)
        # print('\nSCRIPT ARGS:', getattr(module, 'NAME', 'unamed'), args)

        # Return type
        if inspect.isgeneratorfunction(module.run_on):
            pass
        elif inspect.isfunction(module.run_on) and args.annotations.get('return', str) == str:
            pass
        else:
            bad_script_error(module, "run_on object must be a generator of string"
                             " or a function returning a string, not a {}"
                             "".format(type(module.run_on)))

        # Input mode
        first_arg = args.args[0]
        if first_arg == 'context':
            input_mode = str
        elif first_arg == 'models':
            input_mode = iter
        else:
            bad_script_error(module, "run_on first (and only) positional argument"
                             f" must be either 'context' or 'models', not a {first_arg}")

        if len(args.args) != 1:
            # TODO: allows to use regular arguments instead of keyword only
            bad_script_error(module, f"run_on must have only one positional "
                             f"argument, not {len(args.args)}")

        # detect options
        options = []  # list of (arg name, arg type, default, description)
        for arg in args.kwonlyargs:
            argtype = args.annotations.get(arg)
            isgroup = isinstance(argtype, (tuple, list, set, frozenset))
            isrange = isinstance(argtype, range)
            if not isgroup and not isrange and argtype not in OPTIONS_TYPES:
                bad_script_error(module, "Option {} does not have a valid annotation "
                                 "({}). Only tuples, lists, (frozen)sets, and primitive types such as {} are accepted"
                                 "".format(arg, argtype, ', '.join(map(str, OPTIONS_TYPES))))
            if isrange:
                default = (args.kwonlydefaults or {}).get(arg, (argtype.start or 0) if argtype else 0)
            elif isgroup:  # pick an element or a subset of elements as default
                default = (args.kwonlydefaults or {}).get(arg, next(iter(argtype) if argtype else frozenset()))
            else:
                default = (args.kwonlydefaults or {}).get(arg, TYPE_DEFAULT.get(argtype))
            options.append((arg, argtype, default))
        default_options = {arg: default for arg, _, default in options}

        # add the descriptions to options
        options_descriptions = options_description_from_module(
            module, frozenset(default_options.keys()))
        options = tuple((arg, type, default, options_descriptions.get(arg, ''))
                        for arg, type, default in options)
        # TODO: detect non keyword only parameters, and check their validity.

    else:  # no run_on function… the source code and the language will be enough, we hope…
        options, default_options = (), {}
        input_mode = str
        run_on_func = None

    # source code data
    source_code = getattr(module, 'source_code', None)
    language = getattr(module, 'language', 'python')

    # detect trivias
    tags = frozenset(getattr(module, 'TAGS', defaults.get('tags', {'undefined'})))
    doc = DEFAULT_DOC
    if module.__doc__:
        doc = '\n'.join(textwrap.wrap(textwrap.dedent(module.__doc__).strip()))

    # build and return the Script instance
    return Script(
        name=getattr(module, 'NAME', defaults.get('name', 'unamed module')),
        description=doc,
        tags=tags,
        module=module,
        options=tuple(options),
        options_values={},
        input_mode=input_mode,
        incompatible=frozenset(getattr(module, 'INCOMPATIBLE', ())),
        **_build_and_validate_io(module, default_options),
        aggregate=False,
        source_code=source_code,
        language=language,
        erase_context=bool(getattr(module, 'ERASE_CONTEXT', defaults.get('erase_context', False))),
        run_on=run_on_func,
    )


def bad_script_error(script, msg:str):
    """Helper to raise errors while building a script"""
    raise ScriptError(script, "Script/Module {} is not valid. {}."
                      ''.format(script, msg))


def options_description_from_module(module, options, regex=REGEX_OPTION_DESC) -> dict:
    """Return found description for given options in module"""
    if not module.run_on.__doc__: return {}
    ret = {}  # option: description
    lines = module.run_on.__doc__.splitlines(False)
    for line in lines:
        match = regex.fullmatch(line.strip())
        if match:
            name, desc = match.groups()
            if name in options:
                ret[name] = desc.strip()
    return ret


def _build_and_validate_io(module, default_options:dict={}) -> {str: callable}:
    """Return spec_inputs, spec_outputs, inputs and outputs functions
    built from given module.

    module -- the module containing the things
    default_options -- the options to send to inputs and outputs functions

    return -- the dict {field name: function}, usable directly to create
    a Script instance.

    """
    fields = {}  # field name: field value

    IN = lambda *_, **__: frozenset(getattr(module, 'INPUTS', ()))
    OUT = lambda *_, **__: frozenset(getattr(module, 'OUTPUTS', ()))
    fields['spec_inputs'] = getattr(module, 'inputs', IN)
    fields['spec_outputs'] = getattr(module, 'outputs', OUT)
    fields['inputs'] = IN
    fields['outputs'] = OUT


    # Verify that their are functions, and well dev
    for field in ('spec_inputs', 'spec_outputs', 'inputs', 'outputs'):
        func = fields[field]
        if not callable(func):
            bad_script_error(module, 'Attribute {} is not a function'.format(func))
        if not field.startswith('spec_'):  # it's a class method, not an instance one
            retvalue = func()
            if not isinstance(retvalue, (set, frozenset)):
                bad_script_error(module, "Function {} should return a (frozen)set, "
                                 "not {}".format(func.__name__, type(retvalue)))
    return fields
