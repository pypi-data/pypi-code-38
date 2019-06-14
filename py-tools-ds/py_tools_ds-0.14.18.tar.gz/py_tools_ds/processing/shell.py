# -*- coding: utf-8 -*-

import shlex
from subprocess import PIPE, Popen

__author__ = "Daniel Scheffler"


def subcall_with_output(cmd, v=False):
    """Execute external command and get its stdout, exitcode and stderr.

    :param cmd: a normal shell command including parameters
    :param v:   verbose mode (prints
    """
    proc = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()
    exitcode = proc.returncode

    if v and exitcode:
        print('SUBCALL CMD:', cmd)
        print('SUBCALL OUT:', out)
        print('SUBCALL ERR:', err)
    return out, exitcode, err
