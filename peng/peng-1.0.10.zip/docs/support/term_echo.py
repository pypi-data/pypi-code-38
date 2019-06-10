# term_echo.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,R0912,R1717

import os
import platform
import subprocess
import sys


###
# Functions
###
def ste(command, nindent, mdir, fpointer):
    r"""
    Echo terminal output.

    Print STDOUT resulting from a given Bash shell command (relative to the
    package :code:`pypkg` directory) formatted in reStructuredText

    :param command: Bash shell command, relative to
                    :bash:`${PMISC_DIR}/pypkg`
    :type  command: string

    :param nindent: Indentation level
    :type  nindent: integer

    :param mdir: Module directory
    :type  mdir: string

    :param fpointer: Output function pointer. Normally is :code:`cog.out` but
                     :code:`print` or other functions can be used for
                     debugging
    :type  fpointer: function object

    For example::

        .. This is a reStructuredText file snippet
        .. [[[cog
        .. import os, sys
        .. from docs.support.term_echo import term_echo
        .. file_name = sys.modules['docs.support.term_echo'].__file__
        .. mdir = os.path.realpath(
        ..     os.path.dirname(
        ..         os.path.dirname(os.path.dirname(file_name))
        ..     )
        .. )
        .. [[[cog ste('build_docs.py -h', 0, mdir, cog.out) ]]]

        .. code-block:: bash

        $ ${PMISC_DIR}/pypkg/build_docs.py -h
        usage: build_docs.py [-h] [-d DIRECTORY] [-n NUM_CPUS]
        ...

        .. ]]]

    """
    term_echo(
        "${{PMISC_DIR}}{sep}pypkg{sep}{cmd}".format(sep=os.path.sep, cmd=command),
        nindent,
        {"PMISC_DIR": mdir},
        fpointer,
    )


def term_echo(command, nindent=0, env=None, fpointer=None, cols=60):
    """
    Print STDOUT resulting from a Bash shell command formatted in reStructuredText.

    :param command: Bash shell command
    :type  command: string

    :param nindent: Indentation level
    :type  nindent: integer

    :param env: Environment variable replacement dictionary. The Bash
                command is pre-processed and any environment variable
                represented in the full notation (:bash:`${...}`) is replaced.
                The dictionary key is the environment variable name and the
                dictionary value is the replacement value. For example, if
                **command** is :code:`'${PYTHON_CMD} -m "x=5"'` and **env**
                is :code:`{'PYTHON_CMD':'python3'}` the actual command issued
                is :code:`'python3 -m "x=5"'`
    :type  env: dictionary

    :param fpointer: Output function pointer. Normally is :code:`cog.out` but
                     :code:`print` or other functions can be used for
                     debugging
    :type  fpointer: function object

    :param cols: Number of columns of output
    :type  cols: integer
    """
    # pylint: disable=R0204
    # Set argparse width so that output does not need horizontal scroll
    # bar in narrow windows or displays
    os.environ["COLUMNS"] = str(cols)
    command_int = command
    if env:
        for var, repl in env.items():
            command_int = command_int.replace("${" + var + "}", repl)
    tokens = command_int.split(" ")
    # Add Python interpreter executable for Python scripts on Windows since
    # the shebang does not work
    if (platform.system().lower() == "windows") and (tokens[0].endswith(".py")):
        tokens = [sys.executable] + tokens
    proc = subprocess.Popen(tokens, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout = proc.communicate()[0]
    if sys.hexversion >= 0x03000000:
        stdout = stdout.decode("utf-8")
    stdout = stdout.split("\n")
    indent = nindent * " "
    fpointer("\n", dedent=False)
    fpointer("{0}.. code-block:: bash\n".format(indent), dedent=False)
    fpointer("\n", dedent=False)
    fpointer("{0}    $ {1}\n".format(indent, command), dedent=False)
    for line in stdout:
        if line.strip():
            fpointer(indent + "    " + line.replace("\t", "    ") + "\n", dedent=False)
        else:
            fpointer("\n", dedent=False)
    fpointer("\n", dedent=False)
