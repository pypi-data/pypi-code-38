#!/usr/bin/env python
# build_docs.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0411,C0413,E0611,E1129,F0401
# pylint: disable=R0205,R0903,R0912,R0914,R0915,W0141,W1113

# Standard library imports
from __future__ import print_function
import argparse
import datetime
import difflib
import multiprocessing
import os
import platform
import re
import shutil
import sys
import tempfile
import types

# PyPI imports
from cogapp import Cog
import decorator
import docutils
import docutils.core

# Intra-package imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import pypkg.functions

try:
    from pypkg.refresh_moddb import refresh_moddb
except ImportError:

    def refresh_moddb():  # noqa
        pass


try:
    from pypkg.build_moddb import build_moddb
except ImportError:

    def build_moddb():  # noqa
        pass


###
# Global variables
###
VALID_MODULES = [pypkg.functions.get_pkg_name()]
PKG_DOC_SUBMODULES = pypkg.functions.get_pkg_doc_submodules()


###
# Helper classes
###
@decorator.contextmanager
def ignored(*exceptions):
    try:
        yield
    except exceptions:
        pass


class TmpFile(object):
    """
    Use a temporary file within context.

    From pmisc package
    """

    def __init__(self, fpointer=None, *args, **kwargs):  # noqa
        if (
            fpointer
            and (not isinstance(fpointer, types.FunctionType))
            and (not isinstance(fpointer, types.LambdaType))
        ):
            raise RuntimeError("Argument `fpointer` is not valid")
        self._fname = None
        self._fpointer = fpointer
        self._args = args
        self._kwargs = kwargs

    def __enter__(self):  # noqa
        fdesc, fname = tempfile.mkstemp()
        # fdesc is an OS-level file descriptor, see problems if this
        # is not properly closed in this post:
        # https://www.logilab.org/blogentry/17873
        os.close(fdesc)
        if platform.system().lower() == "windows":  # pragma: no cover
            fname = fname.replace(os.sep, "/")
        self._fname = fname
        if self._fpointer:
            with open(self._fname, "w") as fobj:
                self._fpointer(fobj, *self._args, **self._kwargs)
        return self._fname

    def __exit__(self, exc_type, exc_value, exc_tb):  # noqa
        with ignored(OSError):
            os.remove(self._fname)
        return not exc_type is not None


###
# Functions
###
def _get_ex_msg(obj):
    """Get exception message."""
    return obj.value.args[0] if hasattr(obj, "value") else obj.args[0]


def build_pkg_docs(args):
    """Build documentation."""
    debug = False
    retcode = 0
    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_dir = args.directory
    os.environ["NOPTION"] = "-n {0}".format(args.num_cpus) if args.num_cpus > 1 else ""
    rebuild = args.rebuild
    test = args.test
    tracer_dir = os.path.join(pkg_dir, "docs", "support")
    os.environ["TRACER_DIR"] = tracer_dir
    # Processing
    print("Rebuilding documentation")
    if debug:
        print("Python: {0}".format(sys.executable))
        print("PATH: {0}".format(os.environ["PATH"]))
        print("PYTHONPATH: {0}".format(os.environ["PYTHONPATH"]))
        print("functions: {0}".format(pypkg.functions.__file__))
        print("functions.subprocess: {0}".format(pypkg.functions.subprocess.__file__))
    if rebuild or test:
        if not PKG_DOC_SUBMODULES:
            print("No submodules defined, skipping exception documentation rebuilding")
        else:
            refresh_moddb()
            print_cyan(
                "Rebuilding exceptions documentation{0}".format(
                    " (test mode)" if test else ""
                )
            )
            start_time = datetime.datetime.today()
            tmp_retcode = rebuild_module_doc(test, src_dir, tracer_dir)
            retcode = tmp_retcode if not retcode else retcode
            stop_time = datetime.datetime.today()
            print(
                "Elapsed time: {0}".format(elapsed_time_string(start_time, stop_time))
            )
            build_moddb()
    generate_top_level_readme(pkg_dir)
    print("Inserting files into docstrings")
    insert_files_in_rsts(pkg_dir)
    cleanup(pkg_dir)
    print("Generating HTML output")
    shutil.rmtree(os.path.join(pkg_dir, "docs", "_build"), ignore_errors=True)
    cwd = os.getcwd()
    os.chdir(os.path.join(pkg_dir, "docs"))
    pypkg.functions.shcmd(
        [
            "sphinx-build",
            "-b",
            "html",
            "-d",
            os.path.join("_build", "doctrees"),
            "-W",
            ".",
            os.path.join("_build", "html"),
        ],
        "Error building Sphinx documentation",
        async_stdout=True,
    )
    # Copy built documentation to its own directory
    # dest_dir = os.path.join(pkg_dir, 'docs', 'html')
    # src_dir = os.path.join(pkg_dir, 'docs', '_build', 'html')
    # shutil.rmtree(dest_dir, ignore_errors=True)
    # shutil.copytree(src_dir, dest_dir)
    os.chdir(cwd)
    return retcode


def cleanup(pkg_dir):
    """Remove necessary blocks and multiple blank lines."""
    fname = os.path.join(pkg_dir, "README.rst")
    with open(fname, "r") as fobj:
        lines = [item.rstrip() for item in fobj.readlines()]
    remove_block = False
    prev_line = "Start"
    out_lines = []
    for line in lines:
        if line.lstrip().startswith(".. [REMOVE STOP]"):
            remove_block = False
        elif remove_block:
            continue
        elif line.lstrip().startswith(".. [REMOVE START]"):
            remove_block = True
        elif line or ((not line) and prev_line):
            out_lines.append(line)
            prev_line = line.strip()
    with open(fname, "w") as fobj:
        fobj.write("\n".join(out_lines))
    # Check that generated file produces HTML version without errors
    rst2html(os.path.normpath(fname))


def copy_file(src, dest):
    """Copy file (potentially overwriting existing file)."""
    try:
        os.remove(dest)
    except OSError:
        pass
    shutil.copy(src, dest)


def del_file(fname):
    """Delete file."""
    try:
        os.remove(fname)
    except OSError:
        pass


def diff(file1, file2):
    """Diff two files."""
    with open(file1, "r") as fobj1:
        flines1 = [item.rstrip() for item in fobj1.readlines()]
    with open(file2, "r") as fobj2:
        flines2 = [item.rstrip() for item in fobj2.readlines()]
    return list(difflib.unified_diff(flines1, flines2, fromfile=file1, tofile=file2))


def elapsed_time_string(start_time, stop_time):
    """Return a formatted string with the elapsed time between two time points."""
    delta_time = stop_time - start_time
    tot_seconds = int(
        (
            delta_time.microseconds
            + (delta_time.seconds + delta_time.days * 24 * 3600) * 10 ** 6
        )
        / 10 ** 6
    )
    years, remainder = divmod(tot_seconds, 365 * 24 * 60 * 60)
    months, remainder = divmod(remainder, 30 * 24 * 60 * 60)
    days, remainder = divmod(remainder, 24 * 60 * 60)
    hours, remainder = divmod(remainder, 60 * 60)
    minutes, seconds = divmod(remainder, 60)
    token_iter = zip(
        [years, months, days, hours, minutes, seconds],
        ["year", "month", "day", "hour", "minute", "second"],
    )
    ret_list = [
        "{token} {token_name}{plural}".format(
            token=num, token_name=desc, plural="s" if num > 1 else ""
        )
        for num, desc in token_iter
        if num > 0
    ]
    if not ret_list == 0:
        return "None"
    if len(ret_list) == 1:
        return ret_list[0]
    if len(ret_list) == 2:
        return ret_list[0] + " and " + ret_list[1]
    return (", ".join(ret_list[0:-1])) + " and " + ret_list[-1]


def insert_files_in_rsts(pkg_dir):
    """Cog-insert source files in Sphinx files."""
    fnames = [os.path.join(pkg_dir, "README.rst")]
    print("Inserting source files in documentation files")
    for fname in fnames:
        print("   Processing file {0}".format(fname))
        retcode = Cog().main(["cog.py", "-e", "-x", "-o", fname + ".tmp", fname])
        if retcode:
            raise RuntimeError(
                "Error deleting insertion of source files in "
                "documentation file {0}".format(fname)
            )
        retcode = Cog().main(["cog.py", "-e", "-o", fname + ".tmp", fname])
        if retcode:
            raise RuntimeError(
                "Error inserting source files in "
                "docstrings in module {0}".format(fname)
            )
        move_file(fname + ".tmp", fname)


def move_file(src, dest):
    """Copy file (potentially overwriting existing file)."""
    try:
        os.remove(dest)
    except OSError:
        pass
    shutil.move(src, dest)


def pcolor(text, color, indent=0):
    r"""
    Return a string that once printed is colorized.

    :param text: Text to colorize
    :type  text: string

    :param  color: Color to use, one of :code:`'black'`, :code:`'red'`,
                   :code:`'green'`, :code:`'yellow'`, :code:`'blue'`,
                   :code:`'magenta'`, :code:`'cyan'`, :code:`'white'` or
                   :code:`'none'` (case insensitive)
    :type   color: string

    :param indent: Number of spaces to prefix the output with
    :type  indent: integer

    :rtype: string

    :raises:
     * RuntimeError (Argument \`color\` is not valid)

     * RuntimeError (Argument \`indent\` is not valid)

     * RuntimeError (Argument \`text\` is not valid)

     * ValueError (Unknown color *[color]*)
    """
    esc_dict = {
        "black": 30,
        "red": 31,
        "green": 32,
        "yellow": 33,
        "blue": 34,
        "magenta": 35,
        "cyan": 36,
        "white": 37,
        "none": -1,
    }
    if not isinstance(text, str):
        raise RuntimeError("Argument `text` is not valid")
    if not isinstance(color, str):
        raise RuntimeError("Argument `color` is not valid")
    if not isinstance(indent, int):
        raise RuntimeError("Argument `indent` is not valid")
    color = color.lower()
    if color not in esc_dict:
        raise ValueError("Unknown color {color}".format(color=color))
    if esc_dict[color] != -1:
        return "\033[{color_code}m{indent}{text}\033[0m".format(
            color_code=esc_dict[color], indent=" " * indent, text=text
        )
    return "{indent}{text}".format(indent=" " * indent, text=text)


def print_diff(tlist, indent=3):
    """Pretty prints file differences."""
    ret = []
    ret.append((indent * " ") + tlist[0][1:-2])
    ret.append((indent * " ") + tlist[1][1:-2])
    for line in tlist[2:]:
        ret.append((indent * " ") + str(line.rstrip()))
    return "\n".join(ret)


def print_cyan(text):
    """Print text to STDOUT in cyan color."""
    print(pcolor(text, "cyan"))


def print_green(text):
    """Print text to STDOUT in green color."""
    print(pcolor(text, "green"))


def print_red(text):
    """Print text to STDOUT in red color."""
    print(pcolor(text, "red"))


def rebuild_module_doc(test, src_dir, tracer_dir):  # noqa
    # pylint: disable=R0913
    retcode = 0
    pkl_dir = tracer_dir
    submodules = PKG_DOC_SUBMODULES
    for submodule in submodules:
        smf = os.path.join(src_dir, submodule + ".py")
        pkl_file = os.path.join(pkl_dir, submodule + ".pkl")
        print_cyan("Processing module {0}".format(submodule))
        orig_file = smf + ".orig"
        if test:
            shutil.copy(smf, orig_file)
        retcode = Cog().main(["cog.py", "-e", "-o", smf + ".tmp", smf])
        if retcode:
            raise RuntimeError(
                "Error generating exceptions documentation in module {0}".format(smf)
            )
        move_file(smf + ".tmp", smf)
        if test:
            diff_list = diff(smf, orig_file)
            if not diff_list:
                print_green("   File {0} identical from original".format(smf))
                del_file(pkl_file)
            else:
                print_red("   File {0} differs from original".format(smf))
                print("   Differences:")
                print(print_diff(diff_list))
                copy_file(smf, smf + ".error")
                retcode = 1
            move_file(orig_file, smf)
        else:
            del_file(pkl_file)
    return retcode


def rst2html(ifname, desc=""):
    """rst2html.py interface without going through command line."""
    description = (
        "Generates (X)HTML documents from standalone reStructuredText "
        "sources.  " + docutils.core.default_description
    )
    with TmpFile() as ofname:
        sys.argv = [
            "rst2html.py",
            "--exit-status=3",
            "--verbose",
            "--strict",
            ifname,
            ofname,
        ]
        try:
            docutils.core.publish_cmdline(writer_name="html", description=description)
        except (Exception, SystemExit) as exobj:
            ex_msg = "{0}".format(_get_ex_msg(exobj))
            raise RuntimeError(
                (
                    "Error validating top-level{0} README.rst"
                    " HTML conversion:{1}{2}".format(
                        " {0}".format(desc) if desc else "", os.linesep, ex_msg
                    )
                )
            )


def generate_top_level_readme(pkg_dir):
    """
    Remove Sphinx-specific cross-references from top-level README.rst file.

    The references are not rendered by either Bitbucket or GitHub
    """
    # pylint: disable=W0212
    docs_dir = os.path.abspath(os.path.join(pkg_dir, "docs"))
    fname = os.path.join(docs_dir, "README.rst")
    print("Generating top-level README.rst file")
    with open(fname, "r") as fobj:
        lines = [item.rstrip() for item in fobj.readlines()]
    pkg_name = pypkg.functions.get_pkg_name()
    ref1_regexp = re.compile(".*:py:mod:`(.+) <" + pkg_name + ".(.+)>`.*")
    ref2_regexp = re.compile(".*:py:mod:`" + pkg_name + ".(.+)`.*")
    ref3_regexp = re.compile(r".*:ref:`(.+?)(\s+<.+>)*`.*")
    ref4_regexp = re.compile(r".*:py:class:`(.+?)`.*")
    ref5_regexp = re.compile(r".*:py:data:`(.+?)`.*")
    rst_cmd_regexp = re.compile("^\\s*.. \\S+::.*")
    indent_regexp = re.compile("^(\\s*)\\S+")
    ret = []
    autofunction = False
    literalinclude = False
    remove_block = False
    for line in lines:
        match1 = ref1_regexp.match(line)
        match2 = ref2_regexp.match(line)
        match3 = ref3_regexp.match(line)
        match4 = ref4_regexp.match(line)
        match5 = ref5_regexp.match(line)
        if line.lstrip().startswith(".. [REMOVE STOP]"):
            remove_block = False
        elif remove_block:
            continue
        elif autofunction:
            match = indent_regexp.match(line)
            if (not match) or (match and not match.group(1)):
                autofunction = False
                ret.append(line)
        elif literalinclude:
            if line.lstrip().startswith(":lines:"):
                literalinclude = False
                lrange = line.lstrip().replace(":lines:", "").strip()
                extra_dir = "."
                mdir = os.path.join(extra_dir, "docs", "support")
                tstr = (
                    ".. import sys\n"
                    ".. sys.path.append('" + extra_dir + "')\n"
                    ".. import pypkg.incfile\n"
                    ".. cog.outl('.. [REMOVE STOP]')\n"
                    ".. pypkg.incfile.incfile(\n"
                    '..     "{0}",\n'
                    "..     cog.out,\n"
                    '..     "{1}",\n'
                    '..     "' + mdir + '"\n'
                    ".. )\n"
                    ".. cog.outl('.. [REMOVE START]')"
                )
                ret.append(".. [REMOVE START]")
                ret.append(".. [[[cog")
                ret.append(".. import " + pkg_name)
                ret.append(tstr.format(os.path.basename(fname), lrange))
                ret.append(".. ]]]")
                ret.append(".. [[[end]]]")
                ret.append(".. [REMOVE STOP]")
        elif match1:
            # Remove cross-references
            label = match1.group(1)
            mname = match1.group(2)
            line = line.replace(
                ":py:mod:`{label} <".format(label=label)
                + pkg_name
                + ".{mname}>`".format(mname=mname),
                label,
            )
            ret.append(line)
        elif match2:
            # Remove cross-references
            mname = match2.group(1)
            line = line.replace(
                ":py:mod:`" + pkg_name + ".{mname}`".format(mname=mname), mname
            )
            ret.append(line)
        elif match3:
            # Remove cross-references
            mname = match3.group(1)
            target = match3.group(2)
            line = line.replace(
                ":ref:`{mname}{target}`".format(
                    mname=mname, target="" if target is None else target
                ),
                mname,
            )
            ret.append(line)
        elif match4:
            # Remove classes cross-references
            mname = match4.group(1)
            line = line.replace(":py:class:`{mname}`".format(mname=mname), mname)
            ret.append(line)
        elif match5:
            # Remove constants cross-references
            mname = match5.group(1)
            line = line.replace(":py:data:`{mname}`".format(mname=mname), mname)
            ret.append(line)
        elif line.lstrip().startswith(".. literalinclude::"):
            fname = line.lstrip().replace(".. literalinclude::", "").strip()
            literalinclude = True
        elif line.lstrip().startswith(":file:"):
            # csv-table
            fname = line.lstrip().replace(":file:", "").strip()
            ret.append(
                line.replace(fname, os.path.join(".", "docs", "support", "data.csv"))
            )
        elif line.lstrip().startswith(".. include::"):
            # Include files
            base_fname = line.split()[-1].strip()
            fname = os.path.basename(base_fname)
            # Do not include the change log, PyPI adds it at the end
            # of the README.rst file by default and in a hosted Git
            # repository there is a much more detailed built-in change
            # log in the commit message history
            if fname != "CHANGELOG.rst":
                fname = os.path.join(docs_dir, base_fname)
                for inc_line in pypkg.functions._readlines(fname):
                    comment = inc_line.lstrip().startswith(".. ")
                    if (not comment) or (comment and rst_cmd_regexp.match(inc_line)):
                        ret.append(inc_line.rstrip())
        elif line.lstrip().startswith(".. autofunction::"):
            # Remove auto-functions, PyPI reStructuredText parser
            # does not appear to like it
            autofunction = True
        elif line.lstrip().startswith(".. [REMOVE START]"):
            remove_block = True
        else:
            ret.append(line)
    fname = os.path.join(pkg_dir, "README.rst")
    with open(fname, "w") as fobj:
        fobj.write("\n".join(ret))
    # Check that generated file produces HTML version without errors
    rst2html(os.path.normpath(fname))


def valid_dir(value):
    """Argparse checked for directory argument."""
    if not os.path.isdir(value):
        raise argparse.ArgumentTypeError("directory {0} does not exist".format(value))
    return os.path.abspath(value)


def valid_num_cpus(value):
    """Argparse checker for num_cpus argument."""
    # pylint: disable=E1101
    try:
        value = int(value)
    except:
        raise argparse.ArgumentTypeError(
            "invalid positive integer value: {0}".format(value)
        )
    if value < 1:
        raise argparse.ArgumentTypeError(
            "invalid positive integer value: {0}".format(value)
        )
    max_cpus = multiprocessing.cpu_count()
    if value > max_cpus:
        raise argparse.ArgumentTypeError(
            "requested CPUs ({0}) greater than "
            "available CPUs ({1})".format(value, max_cpus)
        )
    return value


if __name__ == "__main__":
    # pylint: disable=E0602
    PKG_NAME = pypkg.functions.get_pkg_name()
    PKG_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PARSER = argparse.ArgumentParser(
        description="Build " + PKG_NAME + " package documentation"
    )
    PARSER.add_argument(
        "-d",
        "--directory",
        help="specify source file directory (default ../" + PKG_NAME + ")",
        type=valid_dir,
        nargs=1,
        default=[os.path.join(PKG_DIR, PKG_NAME)],
    )
    PARSER.add_argument(
        "-r",
        "--rebuild",
        help=(
            "rebuild exceptions documentation. If no module name "
            "is given all modules with auto-generated exceptions "
            "documentation are rebuilt"
        ),
        action="store_true",
    )
    PARSER.add_argument(
        "-n",
        "--num-cpus",
        help="number of CPUs to use (default: 1)",
        type=valid_num_cpus,
        default=1,
    )
    PARSER.add_argument(
        "-t",
        "--test",
        help=(
            "diff original and rebuilt file(s) (exit code 0 "
            "indicates file(s) are identical, exit code 1 "
            "indicates file(s) are different)"
        ),
        action="store_true",
    )
    ARGS = PARSER.parse_args()
    ARGS.directory = ARGS.directory[0]
    if ARGS.rebuild and (not ARGS.test):
        if sys.hexversion < 0x03000000:  # pragma: no cover
            VAR = raw_input("Are you sure [Y/N]? ")
        else:
            VAR = input("Are you sure [Y/N]? ")
        if VAR.lower() != "y":
            sys.exit(0)
    sys.exit(build_pkg_docs(ARGS))
