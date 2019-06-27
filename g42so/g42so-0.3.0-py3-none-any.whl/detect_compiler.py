from distutils.spawn import find_executable
import os
import logging

FLAGS_DICTIONARY = {
    'g++': ['-O2', '-g', '-fPIC', '-shared', '-Wl,-z,defs'],
    'clang++': ['-O2', '-g', '-fPIC', '-shared', '-Wl,-z,defs'],
    }


def compiler_and_flags():
    for comp, flags in FLAGS_DICTIONARY.items():
        exe = find_executable(comp)
        if exe is not None:
            return exe, flags
    else:
        return None, []


def flags(compiler_path):
    compiler_base = os.path.basename(compiler_path)
    for comp, flags in FLAGS_DICTIONARY.items():
        if compiler_base.startswith(comp):
            logging.info('Using compilation flags for {}: {}'
                         .format(comp, flags))
            return flags
    else:
        return []
