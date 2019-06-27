from distutils.spawn import find_executable
from pkgutil import get_data
import subprocess
import shlex
import logging
import inspect
import os
import os.path
import sys
import tempfile

from . import detect_compiler

def get_g42so_detector_wrapper_functions(d_wh, params=''):
    return get_g42so_wrapper_functions(
        d_wh,
        template_basename='detector_wrapper.cc.in',
        varname='aDetector',
        params=params
    )


def get_g42so_pga_wrapper_functions(pga_wh, params=''):
    return get_g42so_wrapper_functions(
        pga_wh,
        template_basename='pga_wrapper.cc.in',
        varname='aPGA',
        params=params
        )


def get_g42so_wrapper_functions(wh, template_basename, varname='a_var',
                               params='/* parameters go here */'):

    template = get_data('g42so', template_basename).decode('utf-8')

    include_directives = ['#include "' + wh[1] + '"']
    includes = '\n'.join(include_directives)

    class_name = wh[0]

    wrapper = template.format(includes=includes,
                              varname=varname,
                              class_name=class_name,
                              params=params
                              )

    return wrapper


def get_dummy_g42so_detector_wrapper_functions():
    return get_g42so_detector_wrapper_functions(
        ('MyDetectorConstruction', 'MyDetectorConstruction.hh')
        )


def get_dummy_g42so_pga_wrapper_functions():
    return get_g42so_pga_wrapper_functions(
        ('MyPrimaryGeneratorAction', 'MyPrimaryGeneratorAction.hh')
        )


def write_temp_wrapper_file(wrapper):
    logging.debug('writing wrapper code: ' + wrapper)

    with tempfile.NamedTemporaryFile(suffix='.cc',
                                     mode='w+',
                                     delete=False) as wrapper_file:

        wrapper_file.write(wrapper)
        wrapper_file.flush()
        wrapper_file.seek(0)

        return wrapper_file.name


def compile(sources, includes, d_wh, pga_wh, output=None, other_flags=None,
            g4config_path=None, custom_detector_wrapper=None,
            custom_pga_wrapper=None, compiler=None, encoding='utf-8'):
    if compiler is None:
        compiler, flags = detect_compiler.compiler_and_flags()
    else:
        flags = detect_compiler.flags(compiler)

    if compiler is None or not flags:
        raise RuntimeError('cannot find compiler or compilation flags')

    # determine the Geant4-specific compilation flags
    if g4config_path:
        g4config = g4config_path
    else:
        g4config = find_executable('geant4-config')
        if not g4config:
            raise RuntimeError('cannot find the geant4-config executable. '
                               'Please specify its location on the command '
                               'line.')
    g4cli = [g4config, '--cflags', '--libs']
    g4process = subprocess.Popen(g4cli, stdout=subprocess.PIPE)
    g4flags_str = g4process.communicate()[0].decode(encoding)
    g4flags = shlex.split(g4flags_str)

    # other flags if present
    if not other_flags:
        other_flags = []

    # include dirs
    include_flags = [item for include in includes for item in ['-I', include]]

    # output file
    if not output:
        output = 'lib' + d_wh[0] + '.so'
    logging.info('Will produce the following output file: ' + output)
    output_flags = ['-o', output]

    if not custom_detector_wrapper:
        detector_wrapper = get_g42so_detector_wrapper_functions(d_wh)
        detector_wrapper_file_name = write_temp_wrapper_file(detector_wrapper)
        sources = [detector_wrapper_file_name] + sources
    else:
        detector_wrapper_file_name = None

    if pga_wh and not custom_pga_wrapper:
        pga_wrapper = get_g42so_pga_wrapper_functions(pga_wh)
        pga_wrapper_file_name = write_temp_wrapper_file(pga_wrapper)
        sources = [pga_wrapper_file_name] + sources
    else:
        pga_wrapper_file_name = None

    version_source = get_data('g42so', 'version.cc')
    with tempfile.NamedTemporaryFile(suffix='.cc',
                                     mode='w+') as version_file:
        sources.append(version_file.name)

        # the CLI to execute
        compiler_cli = [compiler] + \
            flags + \
            include_flags + \
            sources + \
            g4flags + \
            other_flags + \
            output_flags

        try:
            logging.info('Running compilation...')
            logging.debug(' ... compiler CLI: ' + ' '.join(compiler_cli))
            subprocess.check_call(compiler_cli)
        except subprocess.CalledProcessError as err:
            logging.error('Compilation failed with return code {}'
                          .format(err.returncode))
            logging.error('Please inspect the compiler error messages above '
                          'for clues. Maybe you forgot to include a relevant '
                          'source file?')
            sys.exit(1)
        finally:
            if detector_wrapper_file_name:
                os.remove(detector_wrapper_file_name)
            if pga_wrapper_file_name:
                os.remove(pga_wrapper_file_name)
