from os.path import join

import mekpie.messages as messages

from .definitions   import Config, CompilerConfig
from .structure     import get_main_path, get_mekpy_path, get_target_path
from .cc_gcc_clang  import gcc_clang
from .cc_avr_gcc    import avr_gcc
from .cc_emscripten import emscripten
from .cli           import panic
from .util          import (
     tab,
     check_is_file,
     check_is_dir, 
     type_name, 
     exec_str,
     file_as_str,
     smkdir,
)

def get_config(options):
    return config_from_str(options, file_as_str(get_mekpy_path()))

def config_from_str(options, source):
    return config_from_dict(exec_str(source, 'mek.py', {
        'options'        : options,
        'gcc_clang'      : gcc_clang,
        'avr_gcc'        : avr_gcc,
        'emscripten'     : emscripten,
        'CompilerConfig' : CompilerConfig,
    }))

def config_from_dict(config_dict):
    return check_config(Config(**{ key : value
        for key, value
        in config_dict.items()
        if key in Config.keys
    }))

def check_config(config):
    smkdir(get_target_path())
    check_name(config.name)
    check_main(config)
    check_libs(config.libs)
    check_cc(config.cc)
    check_flags(config.flags)
    check_compileflags(config.compileflags)
    check_linkflags(config.linkflags)
    return config

def check_name(name):
    check_type('name', name, str)

def check_main(config):
    check_type('main', config.main, str)
    check_is_file(get_main_path(config.main))

def check_libs(libs):
    check_type('libs', libs, list)
    for lib in libs:
        check_type('libs', lib, str)

def check_cc(cc):
    if hasattr(cc, 'name'):
        check_type('cc.name', cc.name, str)
    else:
        check_type('cc.name', None, str)
    if hasattr(cc, 'compile'):
        check_callable('cc.compile', cc.compile)
    else:
        check_callable('cc.compile', None)
    if hasattr(cc, 'link'):
        check_callable('cc.link', cc.link)
    else:
        check_callable('cc.link', None)
    if hasattr(cc, 'run'):
        check_callable('cc.run', cc.run)
    else:
        check_callable('cc.run', None)
    if hasattr(cc, 'debug'):
        check_callable('cc.debug', cc.debug)
    else:
        check_callable('cc.debug', None)
    if hasattr(cc, 'once'):
        check_callable('cc.once', cc.once)
    else:
        check_callable('cc.once', None)

def check_flags(flags):
    check_type('flags', flags, list)
    for flag in flags:
        check_type('flags', flag, str)

def check_compileflags(compileflags):
    check_type('compilflags', compileflags, list)
    for flag in compileflags:
        check_type('compileflags', flag, str)

def check_linkflags(linkflags):
    check_type('linkflags', linkflags, list)
    for flag in linkflags:
        check_type('linkflags', flag, str)

def check_type(name, value, *expected_types):
    if all([type(value) != exp for exp in expected_types]):
        panic(messages.type_error.format(
            name,
            ' or '.join([exp.__name__ for exp in expected_types]),
            type_name(value),
            tab(get_description(name))
        ))

def check_callable(name, value):
    if not callable(value):
        panic(messages.type_error.format(
            name,
            'callable',
            type_name(value),
            tab(get_description(name))
        ))

def get_description(name):
    return {
        'name'                   : '`name` specifies the name of the project',
        'main'                   : '`main` specifies the .c file continaing `main`',
        'libs'                   : '`libs` speicfies and libraries to load',
        'cc'                     : '`cc` specifies the c compiler configuration to use',
        'cc.name'                : '`cc.name` specifies the name of the compiler configuration',
        'cc.compile'             : '`cc.compile` specifies the compilation function',
        'cc.link'                : '`cc.link` specifies the linking function',
        'cc.run'                 : '`cc.run` specifies the run function',
        'cc.debug'               : '`cc.debug` specifies the debug function',
        'cc.once'                : '`cc.once` is run once per compiler configuration',
        'cmd'                    : '`cmd` specified the c compiler command',
        'dbg'                    : '`dbg` specifies the debugger to use',
        'flags'                  : '`flags` specifies additional compiler and linker flags',
        'compileflags'           : '`compileflags` specifies additional compiler flags',
        'linkflags'              : '`linkflags` specifies additional compiler flags',
    }[name]