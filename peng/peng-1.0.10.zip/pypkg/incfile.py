# incfile.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,R0914

import os


def incfile(fname, fpointer, lrange="1,6-", sdir=None):
    r"""
    Include a Python source file in a docstring formatted in reStructuredText.

    :param fname: File name, relative to environment variable
                  :bash:`${TRACER_DIR}`
    :type  fname: string

    :param fpointer: Output function pointer. Normally is :code:`cog.out` but
                     :code:`print` or other functions can be used for
                     debugging
    :type  fpointer: function object

    :param lrange: Line range to include, similar to Sphinx
                   `literalinclude <http://sphinx-doc.org/markup/code.html
                   #directive-literalinclude>`_ directive
    :type  lrange: string

    :param sdir: Source file directory. If None the :bash:`${TRACER_DIR}`
                 environment variable is used if it is defined, otherwise
                 the directory where the :code:`docs.support.incfile` module
                 is located is used
    :type  sdir: string

    For example:

    .. code-block:: python

        def func():
            \"\"\"
            This is a docstring. This file shows how to use it:

            .. =[=cog
            .. import docs.support.incfile
            .. docs.support.incfile.incfile('func_example.py', cog.out)
            .. =]=
            .. code-block:: python

                # func_example.py
                if __name__ == '__main__':
                    func()

            .. =[=end=]=
            \"\"\"
            return 'This is func output'
    """
    # Read file
    file_dir = (
        sdir
        if sdir
        else os.environ.get("TRACER_DIR", os.path.abspath(os.path.dirname(__file__)))
    )
    fname = os.path.join(file_dir, fname)
    with open(fname) as fobj:
        lines = fobj.readlines()
    # Parse line specification
    tokens = [item.strip() for item in lrange.split(",")]
    inc_lines = []
    for token in tokens:
        if "-" in token:
            subtokens = token.split("-")
            lmin, lmax = (
                int(subtokens[0]),
                int(subtokens[1]) if subtokens[1] else len(lines),
            )
            for num in range(lmin, lmax + 1):
                inc_lines.append(num)
        else:
            inc_lines.append(int(token))
    # Produce output
    fpointer(".. code-block:: python\n")
    fpointer("\n")
    for num, line in enumerate(lines):
        if num + 1 in inc_lines:
            fpointer("    " + line.replace("\t", "    ") if line.strip() else "\n")
    fpointer("\n")
