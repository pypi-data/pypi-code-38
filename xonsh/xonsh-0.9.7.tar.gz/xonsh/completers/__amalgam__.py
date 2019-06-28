"""Amalgamation of xonsh.completers package, made up of the following modules, in order:

* bash_completion
* completer
* pip
* tools
* xompletions
* _aliases
* commands
* man
* path
* python
* base
* bash
* dirs
* init

"""

from sys import modules as _modules
from types import ModuleType as _ModuleType
from importlib import import_module as _import_module


class _LazyModule(_ModuleType):

    def __init__(self, pkg, mod, asname=None):
        '''Lazy module 'pkg.mod' in package 'pkg'.'''
        self.__dct__ = {
            'loaded': False,
            'pkg': pkg,  # pkg
            'mod': mod,  # pkg.mod
            'asname': asname,  # alias
            }

    @classmethod
    def load(cls, pkg, mod, asname=None):
        if mod in _modules:
            key = pkg if asname is None else mod
            return _modules[key]
        else:
            return cls(pkg, mod, asname)

    def __getattribute__(self, name):
        if name == '__dct__':
            return super(_LazyModule, self).__getattribute__(name)
        dct = self.__dct__
        mod = dct['mod']
        if dct['loaded']:
            m = _modules[mod]
        else:
            m = _import_module(mod)
            glbs = globals()
            pkg = dct['pkg']
            asname = dct['asname']
            if asname is None:
                glbs[pkg] = m = _modules[pkg]
            else:
                glbs[asname] = m
            dct['loaded'] = True
        return getattr(m, name)

#
# bash_completion
#
"""This module provides the implementation for the retrieving completion results
from bash.
"""
# developer note: this file should not perform any action on import.
#                 This file comes from https://github.com/xonsh/py-bash-completion
#                 and should be edited there!
os = _LazyModule.load('os', 'os')
re = _LazyModule.load('re', 're')
sys = _LazyModule.load('sys', 'sys')
shlex = _LazyModule.load('shlex', 'shlex')
shutil = _LazyModule.load('shutil', 'shutil')
pathlib = _LazyModule.load('pathlib', 'pathlib')
platform = _LazyModule.load('platform', 'platform')
functools = _LazyModule.load('functools', 'functools')
subprocess = _LazyModule.load('subprocess', 'subprocess')
__version__ = "0.2.6"


@functools.lru_cache(1)
def _git_for_windows_path():
    """Returns the path to git for windows, if available and None otherwise."""
    import winreg

    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\GitForWindows")
        gfwp, _ = winreg.QueryValueEx(key, "InstallPath")
    except FileNotFoundError:
        gfwp = None
    return gfwp


@functools.lru_cache(1)
def _windows_bash_command(env=None):
    """Determines the command for Bash on windows."""
    wbc = "bash"
    path = None if env is None else env.get("PATH", None)
    bash_on_path = shutil.which("bash", path=path)
    if bash_on_path:
        try:
            out = subprocess.check_output(
                [bash_on_path, "--version"],
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
        except subprocess.CalledProcessError:
            bash_works = False
        else:
            # Check if Bash is from the "Windows Subsystem for Linux" (WSL)
            # which can't be used by xonsh foreign-shell/completer
            bash_works = out and "pc-linux-gnu" not in out.splitlines()[0]

        if bash_works:
            wbc = bash_on_path
        else:
            gfwp = _git_for_windows_path()
            if gfwp:
                bashcmd = os.path.join(gfwp, "bin\\bash.exe")
                if os.path.isfile(bashcmd):
                    wbc = bashcmd
    return wbc


def _bash_command(env=None):
    """Determines the command for Bash on the current plaform."""
    if platform.system() == "Windows":
        bc = _windows_bash_command(env=None)
    else:
        bc = "bash"
    return bc


def _bash_completion_paths_default():
    """A possibly empty tuple with default paths to Bash completions known for
    the current platform.
    """
    platform_sys = platform.system()
    if platform_sys == "Linux" or sys.platform == "cygwin":
        bcd = ("/usr/share/bash-completion/bash_completion",)
    elif platform_sys == "Darwin":
        bcd = (
            "/usr/local/share/bash-completion/bash_completion",  # v2.x
            "/usr/local/etc/bash_completion",
        )  # v1.x
    elif platform_sys == "Windows":
        gfwp = _git_for_windows_path()
        if gfwp:
            bcd = (
                os.path.join(gfwp, "usr\\share\\bash-completion\\" "bash_completion"),
                os.path.join(
                    gfwp, "mingw64\\share\\git\\completion\\" "git-completion.bash"
                ),
            )
        else:
            bcd = ()
    else:
        bcd = ()
    return bcd


_BASH_COMPLETIONS_PATHS_DEFAULT = None


def _get_bash_completions_source(paths=None):
    global _BASH_COMPLETIONS_PATHS_DEFAULT
    if paths is None:
        if _BASH_COMPLETIONS_PATHS_DEFAULT is None:
            _BASH_COMPLETIONS_PATHS_DEFAULT = _bash_completion_paths_default()
        paths = _BASH_COMPLETIONS_PATHS_DEFAULT
    for path in map(pathlib.Path, paths):
        if path.is_file():
            return 'source "{}"'.format(path.as_posix())
    return None


def _bash_get_sep():
    """ Returns the appropriate filepath separator char depending on OS and
    xonsh options set
    """
    if platform.system() == "Windows":
        return os.altsep
    else:
        return os.sep


_BASH_PATTERN_NEED_QUOTES = None


def _bash_pattern_need_quotes():
    global _BASH_PATTERN_NEED_QUOTES
    if _BASH_PATTERN_NEED_QUOTES is not None:
        return _BASH_PATTERN_NEED_QUOTES
    pattern = r'\s`\$\{\}\,\*\(\)"\'\?&'
    if platform.system() == "Windows":
        pattern += "%"
    pattern = "[" + pattern + "]" + r"|\band\b|\bor\b"
    _BASH_PATTERN_NEED_QUOTES = re.compile(pattern)
    return _BASH_PATTERN_NEED_QUOTES


def _bash_expand_path(s):
    """Takes a string path and expands ~ to home and environment vars."""
    # expand ~ according to Bash unquoted rules "Each variable assignment is
    # checked for unquoted tilde-prefixes immediately following a ':' or the
    # first '='". See the following for more details.
    # https://www.gnu.org/software/bash/manual/html_node/Tilde-Expansion.html
    pre, char, post = s.partition("=")
    if char:
        s = os.path.expanduser(pre) + char
        s += os.pathsep.join(map(os.path.expanduser, post.split(os.pathsep)))
    else:
        s = os.path.expanduser(s)
    return s


def _bash_quote_to_use(x):
    single = "'"
    double = '"'
    if single in x and double not in x:
        return double
    else:
        return single


def _bash_quote_paths(paths, start, end):
    out = set()
    space = " "
    backslash = "\\"
    double_backslash = "\\\\"
    slash = _bash_get_sep()
    orig_start = start
    orig_end = end
    # quote on all or none, to make readline completes to max prefix
    need_quotes = any(
        re.search(_bash_pattern_need_quotes(), x)
        or (backslash in x and slash != backslash)
        for x in paths
    )

    for s in paths:
        start = orig_start
        end = orig_end
        if start == "" and need_quotes:
            start = end = _bash_quote_to_use(s)
        if os.path.isdir(_bash_expand_path(s)):
            _tail = slash
        elif end == "":
            _tail = space
        else:
            _tail = ""
        if start != "" and "r" not in start and backslash in s:
            start = "r%s" % start
        s = s + _tail
        if end != "":
            if "r" not in start.lower():
                s = s.replace(backslash, double_backslash)
            if s.endswith(backslash) and not s.endswith(double_backslash):
                s += backslash
        if end in s:
            s = s.replace(end, "".join("\\%s" % i for i in end))
        out.add(start + s + end)
    return out, need_quotes


BASH_COMPLETE_SCRIPT = r"""
{source}

# Override some functions in bash-completion, do not quote for readline
quote_readline()
{{
    echo "$1"
}}

_quote_readline_by_ref()
{{
    if [[ $1 == \'* || $1 == \"* ]]; then
        # Leave out first character
        printf -v $2 %s "${{1:1}}"
    else
        printf -v $2 %s "$1"
    fi

    [[ ${{!2}} == \$* ]] && eval $2=${{!2}}
}}


function _get_complete_statement {{
    complete -p {cmd} 2> /dev/null || echo "-F _minimal"
}}

function getarg {{
    find=$1
    shift 1
    prev=""
    for i in $* ; do
        if [ "$prev" = "$find" ] ; then
            echo $i
        fi
        prev=$i
    done
}}

_complete_stmt=$(_get_complete_statement)
if echo "$_complete_stmt" | grep --quiet -e "_minimal"
then
    declare -f _completion_loader > /dev/null && _completion_loader {cmd}
    _complete_stmt=$(_get_complete_statement)
fi

# Is -C (subshell) or -F (function) completion used?
if [[ $_complete_stmt =~ "-C" ]] ; then
    _func=$(eval getarg "-C" $_complete_stmt)
else
    _func=$(eval getarg "-F" $_complete_stmt)
    declare -f "$_func" > /dev/null || exit 1
fi

echo "$_complete_stmt"
export COMP_WORDS=({line})
export COMP_LINE={comp_line}
export COMP_POINT=${{#COMP_LINE}}
export COMP_COUNT={end}
export COMP_CWORD={n}
$_func {cmd} {prefix} {prev}

# print out completions, right-stripped if they contain no internal spaces
shopt -s extglob
for ((i=0;i<${{#COMPREPLY[*]}};i++))
do
    no_spaces="${{COMPREPLY[i]//[[:space:]]}}"
    no_trailing_spaces="${{COMPREPLY[i]%%+([[:space:]])}}"
    if [[ "$no_spaces" == "$no_trailing_spaces" ]]; then
        echo "$no_trailing_spaces"
    else
        echo "${{COMPREPLY[i]}}"
    fi
done
"""


def bash_completions(
    prefix,
    line,
    begidx,
    endidx,
    env=None,
    paths=None,
    command=None,
    quote_paths=_bash_quote_paths,
    **kwargs
):
    """Completes based on results from BASH completion.

    Parameters
    ----------
    prefix : str
        The string to match
    line : str
        The line that prefix appears on.
    begidx : int
        The index in line that prefix starts on.
    endidx : int
        The index in line that prefix ends on.
    env : Mapping, optional
        The environment dict to execute the Bash subprocess in.
    paths : list or tuple of str or None, optional
        This is a list (or tuple) of strings that specifies where the
        ``bash_completion`` script may be found. The first valid path will
        be used. For better performance, bash-completion v2.x is recommended
        since it lazy-loads individual completion scripts. For both
        bash-completion v1.x and v2.x, paths of individual completion scripts
        (like ``.../completes/ssh``) do not need to be included here. The
        default values are platform dependent, but sane.
    command : str or None, optional
        The /path/to/bash to use. If None, it will be selected based on the
        from the environment and platform.
    quote_paths : callable, optional
        A functions that quotes file system paths. You shouldn't normally need
        this as the default is acceptable 99+% of the time. This function should
        return a set of the new paths and a boolean for whether the paths were
        quoted.

    Returns
    -------
    rtn : set of str
        Possible completions of prefix
    lprefix : int
        Length of the prefix to be replaced in the completion.
    """
    source = _get_bash_completions_source(paths) or ""

    if prefix.startswith("$"):  # do not complete env variables
        return set(), 0

    splt = line.split()
    cmd = splt[0]
    idx = n = 0
    prev = ""
    for n, tok in enumerate(splt):
        if tok == prefix:
            idx = line.find(prefix, idx)
            if idx >= begidx:
                break
        prev = tok

    if len(prefix) == 0:
        prefix_quoted = '""'
        n += 1
    else:
        prefix_quoted = shlex.quote(prefix)

    script = BASH_COMPLETE_SCRIPT.format(
        source=source,
        line=" ".join(shlex.quote(p) for p in splt),
        comp_line=shlex.quote(line),
        n=n,
        cmd=shlex.quote(cmd),
        end=endidx + 1,
        prefix=prefix_quoted,
        prev=shlex.quote(prev),
    )

    if command is None:
        command = _bash_command(env=env)
    try:
        out = subprocess.check_output(
            [command, "-c", script],
            universal_newlines=True,
            stderr=subprocess.PIPE,
            env=env,
        )
        if not out:
            raise ValueError
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        UnicodeDecodeError,
        ValueError,
    ):
        return set(), 0

    out = out.splitlines()
    complete_stmt = out[0]
    out = set(out[1:])

    # From GNU Bash document: The results of the expansion are prefix-matched
    # against the word being completed

    # Ensure input to `commonprefix` is a list (now required by Python 3.6)
    commprefix = os.path.commonprefix(list(out))
    strip_len = 0
    strip_prefix = prefix.strip("\"'")
    while strip_len < len(strip_prefix) and strip_len < len(commprefix):
        if commprefix[strip_len] == strip_prefix[strip_len]:
            break
        strip_len += 1

    if "-o noquote" not in complete_stmt:
        out, need_quotes = quote_paths(out, "", "")
    if "-o nospace" in complete_stmt:
        out = set([x.rstrip() for x in out])

    return out, max(len(prefix) - strip_len, 0)


def bash_complete_line(line, return_line=True, **kwargs):
    """Provides the completion from the end of the line.

    Parameters
    ----------
    line : str
        Line to complete
    return_line : bool, optional
        If true (default), will return the entire line, with the completion added.
        If false, this will instead return the strings to append to the original line.
    kwargs : optional
        All other keyword arguments are passed to the bash_completions() function.

    Returns
    -------
    rtn : set of str
        Possible completions of prefix
    """
    # set up for completing from the end of the line
    split = line.split()
    if len(split) > 1 and not line.endswith(" "):
        prefix = split[-1]
        begidx = len(line.rsplit(prefix)[0])
    else:
        prefix = ""
        begidx = len(line)
    endidx = len(line)
    # get completions
    out, lprefix = bash_completions(prefix, line, begidx, endidx, **kwargs)
    # reformat output
    if return_line:
        preline = line[:-lprefix]
        rtn = {preline + o for o in out}
    else:
        rtn = {o[lprefix:] for o in out}
    return rtn


def _bc_main(args=None):
    """Runs complete_line() and prints the output."""
    from argparse import ArgumentParser

    p = ArgumentParser("bash_completions")
    p.add_argument(
        "--return-line",
        action="store_true",
        dest="return_line",
        default=True,
        help="will return the entire line, with the completion added",
    )
    p.add_argument(
        "--no-return-line",
        action="store_false",
        dest="return_line",
        help="will instead return the strings to append to the original line",
    )
    p.add_argument("line", help="line to complete")
    ns = p.parse_args(args=args)
    out = bash_complete_line(ns.line, return_line=ns.return_line)
    for o in sorted(out):
        print(o)


if __name__ == "__main__":
    _bc_main()

#
# completer
#
builtins = _LazyModule.load('builtins', 'builtins')
def complete_completer(prefix, line, start, end, ctx):
    """
    Completion for "completer"
    """
    args = line.split(" ")
    if len(args) == 0 or args[0] != "completer":
        return None
    curix = args.index(prefix)
    compnames = set(builtins.__xonsh__.completers.keys())
    if curix == 1:
        possible = {"list", "help", "add", "remove"}
    elif curix == 2:
        if args[1] == "help":
            possible = {"list", "add", "remove"}
        elif args[1] == "remove":
            possible = compnames
        else:
            raise StopIteration
    else:
        if args[1] != "add":
            raise StopIteration
        if curix == 3:
            possible = {i for i, j in builtins.__xonsh__.ctx.items() if callable(j)}
        elif curix == 4:
            possible = (
                {"start", "end"}
                | {">" + n for n in compnames}
                | {"<" + n for n in compnames}
            )
        else:
            raise StopIteration
    return {i for i in possible if i.startswith(prefix)}

#
# pip
#
"""Completers for pip."""
# pylint: disable=invalid-name, missing-docstring, unsupported-membership-test
# pylint: disable=unused-argument, not-an-iterable
# amalgamated re
# amalgamated subprocess
xl = _LazyModule.load('xonsh', 'xonsh.lazyasd', 'xl')
@xl.lazyobject
def PIP_RE():
    return re.compile(r"\bx?pip(?:\d|\.)*")


@xl.lazyobject
def PIP_LIST_RE():
    return re.compile(r"\bx?pip(?:\d|\.)* (?:uninstall|show)")


@xl.lazyobject
def ALL_COMMANDS():
    try:
        help_text = str(
            subprocess.check_output(["pip", "--help"], stderr=subprocess.DEVNULL)
        )
    except FileNotFoundError:
        return []
    commands = re.findall(r"  (\w+)  ", help_text)
    return [c for c in commands if c not in ["completion", "help"]]


def complete_pip(prefix, line, begidx, endidx, ctx):
    """Completes python's package manager pip"""
    line_len = len(line.split())
    if (
        (line_len > 3)
        or (line_len > 2 and line.endswith(" "))
        or (not PIP_RE.search(line))
    ):
        return
    if PIP_LIST_RE.search(line):
        try:
            items = subprocess.check_output(["pip", "list"], stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            return set()
        items = items.decode("utf-8").splitlines()
        return set(i.split()[0] for i in items if i.split()[0].startswith(prefix))

    if (line_len > 1 and line.endswith(" ")) or line_len > 2:
        # "pip show " -> no complete (note space)
        return
    if prefix not in ALL_COMMANDS:
        suggestions = [c for c in ALL_COMMANDS if c.startswith(prefix)]
        if suggestions:
            return suggestions, len(prefix)
    return ALL_COMMANDS, len(prefix)

#
# tools
#
"""Xonsh completer tools."""
# amalgamated builtins
textwrap = _LazyModule.load('textwrap', 'textwrap')
def _filter_normal(s, x):
    return s.startswith(x)


def _filter_ignorecase(s, x):
    return s.lower().startswith(x.lower())


def get_filter_function():
    """
    Return an appropriate filtering function for completions, given the valid
    of $CASE_SENSITIVE_COMPLETIONS
    """
    csc = builtins.__xonsh__.env.get("CASE_SENSITIVE_COMPLETIONS")
    if csc:
        return _filter_normal
    else:
        return _filter_ignorecase


def justify(s, max_length, left_pad=0):
    """
    Re-wrap the string s so that each line is no more than max_length
    characters long, padding all lines but the first on the left with the
    string left_pad.
    """
    txt = textwrap.wrap(s, width=max_length, subsequent_indent=" " * left_pad)
    return "\n".join(txt)

#
# xompletions
#
"""Provides completions for xonsh internal utilities"""

xx = _LazyModule.load('xonsh', 'xonsh.xontribs', 'xx')
xt = _LazyModule.load('xonsh', 'xonsh.tools', 'xt')
def complete_xonfig(prefix, line, start, end, ctx):
    """Completion for ``xonfig``"""
    args = line.split(" ")
    if len(args) == 0 or args[0] != "xonfig":
        return None
    curix = args.index(prefix)
    if curix == 1:
        possible = {"info", "wizard", "styles", "colors", "-h"}
    elif curix == 2 and args[1] == "colors":
        possible = set(xt.color_style_names())
    else:
        raise StopIteration
    return {i for i in possible if i.startswith(prefix)}


def _list_installed_xontribs():
    meta = xx.xontrib_metadata()
    installed = []
    for md in meta["xontribs"]:
        name = md["name"]
        spec = xx.find_xontrib(name)
        if spec is not None:
            installed.append(spec.name.rsplit(".")[-1])

    return installed


def complete_xontrib(prefix, line, start, end, ctx):
    """Completion for ``xontrib``"""
    args = line.split(" ")
    if len(args) == 0 or args[0] != "xontrib":
        return None
    curix = args.index(prefix)
    if curix == 1:
        possible = {"list", "load"}
    elif curix == 2:
        if args[1] == "load":
            possible = _list_installed_xontribs()
    else:
        raise StopIteration

    return {i for i in possible if i.startswith(prefix)}

#
# _aliases
#
# amalgamated builtins
collections = _LazyModule.load('collections', 'collections')
# amalgamated xonsh.lazyasd
# amalgamated xonsh.completers.tools
VALID_ACTIONS = xl.LazyObject(
    lambda: frozenset({"add", "remove", "list"}), globals(), "VALID_ACTIONS"
)


def _add_one_completer(name, func, loc="end"):
    new = collections.OrderedDict()
    if loc == "start":
        new[name] = func
        for (k, v) in builtins.__xonsh__.completers.items():
            new[k] = v
    elif loc == "end":
        for (k, v) in builtins.__xonsh__.completers.items():
            new[k] = v
        new[name] = func
    else:
        direction, rel = loc[0], loc[1:]
        found = False
        for (k, v) in builtins.__xonsh__.completers.items():
            if rel == k and direction == "<":
                new[name] = func
                found = True
            new[k] = v
            if rel == k and direction == ">":
                new[name] = func
                found = True
        if not found:
            new[name] = func
    builtins.__xonsh__.completers.clear()
    builtins.__xonsh__.completers.update(new)


def _list_completers(args, stdin=None, stack=None):
    o = "Registered Completer Functions: \n"
    _comp = builtins.__xonsh__.completers
    ml = max((len(i) for i in _comp), default=0)
    _strs = []
    for c in _comp:
        if _comp[c].__doc__ is None:
            doc = "No description provided"
        else:
            doc = " ".join(_comp[c].__doc__.split())
        doc = justify(doc, 80, ml + 3)
        _strs.append("{: >{}} : {}".format(c, ml, doc))
    return o + "\n".join(_strs) + "\n"


def _remove_completer(args, stdin=None, stack=None):
    err = None
    if len(args) != 1:
        err = "completer remove takes exactly 1 argument."
    else:
        name = args[0]
        if name not in builtins.__xonsh__.completers:
            err = ("The name %s is not a registered " "completer function.") % name
    if err is None:
        del builtins.__xonsh__.completers[name]
        return
    else:
        return None, err + "\n", 1


def _register_completer(args, stdin=None, stack=None):
    err = None
    if len(args) not in {2, 3}:
        err = (
            "completer add takes either 2 or 3 arguments.\n"
            "For help, run:  completer help add"
        )
    else:
        name = args[0]
        func_name = args[1]
        if name in builtins.__xonsh__.completers:
            err = ("The name %s is already a registered " "completer function.") % name
        else:
            if func_name in builtins.__xonsh__.ctx:
                func = builtins.__xonsh__.ctx[func_name]
                if not callable(func):
                    err = "%s is not callable" % func_name
            else:
                for frame_info in stack:
                    frame = frame_info[0]
                    if func_name in frame.f_locals:
                        func = frame.f_locals[func_name]
                        break
                    elif func_name in frame.f_globals:
                        func = frame.f_globals[func_name]
                        break
                else:
                    err = "No such function: %s" % func_name
    if err is None:
        position = "start" if len(args) == 2 else args[2]
        _add_one_completer(name, func, position)
    else:
        return None, err + "\n", 1


def completer_alias(args, stdin=None, stdout=None, stderr=None, spec=None, stack=None):
    err = None
    if len(args) == 0 or args[0] not in (VALID_ACTIONS | {"help"}):
        err = (
            "Please specify an action.  Valid actions are: "
            '"add", "remove", "list", or "help".'
        )
    elif args[0] == "help":
        if len(args) == 1 or args[1] not in VALID_ACTIONS:
            return (
                "Valid actions are: add, remove, list.  For help with a "
                "specific action, run: completer help ACTION\n"
            )
        elif args[1] == "add":
            return COMPLETER_ADD_HELP_STR
        elif args[1] == "remove":
            return COMPLETER_REMOVE_HELP_STR
        elif args[1] == "list":
            return COMPLETER_LIST_HELP_STR

    if err is not None:
        return None, err + "\n", 1

    if args[0] == "add":
        func = _register_completer
    elif args[0] == "remove":
        func = _remove_completer
    elif args[0] == "list":
        func = _list_completers
    return func(args[1:], stdin=stdin, stack=stack)


COMPLETER_LIST_HELP_STR = """completer list: ordered list the active completers

Usage:
    completer remove
"""

COMPLETER_REMOVE_HELP_STR = """completer remove: removes a completer from xonsh

Usage:
    completer remove NAME

NAME is a unique name of a completer (run "completer list" to see the current
     completers in order)
"""

COMPLETER_ADD_HELP_STR = """completer add: adds a new completer to xonsh

Usage:
    completer add NAME FUNC [POS]

NAME is a unique name to use in the listing (run "completer list" to see the
     current completers in order)

FUNC is the name of a completer function to use.  This should be a function
     of the following arguments, and should return a set of valid completions
     for the given prefix.  If this completer should not be used in a given
     context, it should return an empty set or None.

     Arguments to FUNC:
       * prefix: the string to be matched
       * line: a string representing the whole current line, for context
       * begidx: the index at which prefix starts in line
       * endidx: the index at which prefix ends in line
       * ctx: the current Python environment

     If the completer expands the prefix in any way, it should return a tuple
     of two elements: the first should be the set of completions, and the
     second should be the length of the modified prefix (for an example, see
     xonsh.completers.path.complete_path).

POS (optional) is a position into the list of completers at which the new
     completer should be added.  It can be one of the following values:
       * "start" indicates that the completer should be added to the start of
                 the list of completers (it should be run before all others)
       * "end" indicates that the completer should be added to the end of the
               list of completers (it should be run after all others)
       * ">KEY", where KEY is a pre-existing name, indicates that this should
                 be added after the completer named KEY
       * "<KEY", where KEY is a pre-existing name, indicates that this should
                 be added before the completer named KEY

     If POS is not provided, the default value is "start"
"""

#
# commands
#
# amalgamated os
# amalgamated builtins
# amalgamated xonsh.tools
xp = _LazyModule.load('xonsh', 'xonsh.platform', 'xp')
# amalgamated xonsh.completers.tools
SKIP_TOKENS = {"sudo", "time", "timeit", "which", "showcmd", "man"}
END_PROC_TOKENS = {"|", "||", "&&", "and", "or"}


def complete_command(cmd, line, start, end, ctx):
    """
    Returns a list of valid commands starting with the first argument
    """
    space = " "
    out = {
        s + space
        for s in builtins.__xonsh__.commands_cache
        if get_filter_function()(s, cmd)
    }
    if xp.ON_WINDOWS:
        out |= {i for i in xt.executables_in(".") if i.startswith(cmd)}
    base = os.path.basename(cmd)
    if os.path.isdir(base):
        out |= {
            os.path.join(base, i) for i in xt.executables_in(base) if i.startswith(cmd)
        }
    return out


def complete_skipper(cmd, line, start, end, ctx):
    """
    Skip over several tokens (e.g., sudo) and complete based on the rest of the
    line.
    """
    parts = line.split(" ")
    skip_part_num = 0
    for i, s in enumerate(parts):
        if s in END_PROC_TOKENS:
            skip_part_num = i + 1
    while len(parts) > skip_part_num:
        if parts[skip_part_num] not in SKIP_TOKENS:
            break
        skip_part_num += 1

    if skip_part_num == 0:
        return set()

    # If there's no space following an END_PROC_TOKEN, insert one
    if parts[-1] in END_PROC_TOKENS:
        return (set(" "), 0)

    if len(parts) == skip_part_num + 1:
        comp_func = complete_command
    else:
        comp = builtins.__xonsh__.shell.shell.completer
        comp_func = comp.complete

    skip_len = len(" ".join(line[:skip_part_num])) + 1
    return comp_func(
        cmd, " ".join(parts[skip_part_num:]), start - skip_len, end - skip_len, ctx
    )

#
# man
#
# amalgamated os
# amalgamated re
pickle = _LazyModule.load('pickle', 'pickle')
# amalgamated builtins
# amalgamated subprocess
# amalgamated xonsh.lazyasd
# amalgamated xonsh.completers.tools
OPTIONS = None
OPTIONS_PATH = None


@xl.lazyobject
def SCRAPE_RE():
    return re.compile(r"^(?:\s*(?:-\w|--[a-z0-9-]+)[\s,])+", re.M)


@xl.lazyobject
def INNER_OPTIONS_RE():
    return re.compile(r"-\w|--[a-z0-9-]+")


def complete_from_man(prefix, line, start, end, ctx):
    """
    Completes an option name, based on the contents of the associated man
    page.
    """
    global OPTIONS, OPTIONS_PATH
    if OPTIONS is None:
        datadir = builtins.__xonsh__.env["XONSH_DATA_DIR"]
        OPTIONS_PATH = os.path.join(datadir, "man_completions_cache")
        try:
            with open(OPTIONS_PATH, "rb") as f:
                OPTIONS = pickle.load(f)
        except Exception:
            OPTIONS = {}
    if not prefix.startswith("-"):
        return set()
    cmd = line.split()[0]
    if cmd not in OPTIONS:
        try:
            manpage = subprocess.Popen(
                ["man", cmd], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
            )
            # This is a trick to get rid of reverse line feeds
            text = subprocess.check_output(["col", "-b"], stdin=manpage.stdout)
            text = text.decode("utf-8")
            scraped_text = " ".join(SCRAPE_RE.findall(text))
            matches = INNER_OPTIONS_RE.findall(scraped_text)
            OPTIONS[cmd] = matches
            with open(OPTIONS_PATH, "wb") as f:
                pickle.dump(OPTIONS, f)
        except Exception:
            return set()
    return {s for s in OPTIONS[cmd] if get_filter_function()(s, prefix)}

#
# path
#
# amalgamated os
# amalgamated re
ast = _LazyModule.load('ast', 'ast')
glob = _LazyModule.load('glob', 'glob')
# amalgamated builtins
# amalgamated xonsh.tools
# amalgamated xonsh.platform
# amalgamated xonsh.lazyasd
# amalgamated xonsh.completers.tools
@xl.lazyobject
def PATTERN_NEED_QUOTES():
    pattern = r'\s`\$\{\}\,\*\(\)"\'\?&#'
    if xp.ON_WINDOWS:
        pattern += "%"
    pattern = "[" + pattern + "]" + r"|\band\b|\bor\b"
    return re.compile(pattern)


def cd_in_command(line):
    """Returns True if "cd" is a token in the line, False otherwise."""
    lexer = builtins.__xonsh__.execer.parser.lexer
    lexer.reset()
    lexer.input(line)
    have_cd = False
    for tok in lexer:
        if tok.type == "NAME" and tok.value == "cd":
            have_cd = True
            break
    return have_cd


def _path_from_partial_string(inp, pos=None):
    if pos is None:
        pos = len(inp)
    partial = inp[:pos]
    startix, endix, quote = xt.check_for_partial_string(partial)
    _post = ""
    if startix is None:
        return None
    elif endix is None:
        string = partial[startix:]
    else:
        if endix != pos:
            _test = partial[endix:pos]
            if not any(i == " " for i in _test):
                _post = _test
            else:
                return None
        string = partial[startix:endix]
    end = xt.RE_STRING_START.sub("", quote)
    _string = string
    if not _string.endswith(end):
        _string = _string + end
    try:
        val = ast.literal_eval(_string)
    except (SyntaxError, ValueError):
        return None
    if isinstance(val, bytes):
        env = builtins.__xonsh__.env
        val = val.decode(
            encoding=env.get("XONSH_ENCODING"), errors=env.get("XONSH_ENCODING_ERRORS")
        )
    return string + _post, val + _post, quote, end


def _normpath(p):
    """
    Wraps os.normpath() to avoid removing './' at the beginning
    and '/' at the end. On windows it does the same with backslashes
    """
    initial_dotslash = p.startswith(os.curdir + os.sep)
    initial_dotslash |= xp.ON_WINDOWS and p.startswith(os.curdir + os.altsep)
    p = p.rstrip()
    trailing_slash = p.endswith(os.sep)
    trailing_slash |= xp.ON_WINDOWS and p.endswith(os.altsep)
    p = os.path.normpath(p)
    if initial_dotslash and p != ".":
        p = os.path.join(os.curdir, p)
    if trailing_slash:
        p = os.path.join(p, "")
    if xp.ON_WINDOWS and builtins.__xonsh__.env.get("FORCE_POSIX_PATHS"):
        p = p.replace(os.sep, os.altsep)
    return p


def _startswithlow(x, start, startlow=None):
    if startlow is None:
        startlow = start.lower()
    return x.startswith(start) or x.lower().startswith(startlow)


def _startswithnorm(x, start, startlow=None):
    return x.startswith(start)


def _env(prefix):
    if prefix.startswith("$"):
        key = prefix[1:]
        return {
            "$" + k for k in builtins.__xonsh__.env if get_filter_function()(k, key)
        }
    return ()


def _dots(prefix):
    slash = xt.get_sep()
    if slash == "\\":
        slash = ""
    if prefix in {"", "."}:
        return ("." + slash, ".." + slash)
    elif prefix == "..":
        return (".." + slash,)
    else:
        return ()


def _add_cdpaths(paths, prefix):
    """Completes current prefix using CDPATH"""
    env = builtins.__xonsh__.env
    csc = env.get("CASE_SENSITIVE_COMPLETIONS")
    glob_sorted = env.get("GLOB_SORTED")
    for cdp in env.get("CDPATH"):
        test_glob = os.path.join(cdp, prefix) + "*"
        for s in xt.iglobpath(
            test_glob, ignore_case=(not csc), sort_result=glob_sorted
        ):
            if os.path.isdir(s):
                paths.add(os.path.basename(s))


def _quote_to_use(x):
    single = "'"
    double = '"'
    if single in x and double not in x:
        return double
    else:
        return single


def _quote_paths(paths, start, end, append_end=True):
    expand_path = builtins.__xonsh__.expand_path
    out = set()
    space = " "
    backslash = "\\"
    double_backslash = "\\\\"
    slash = xt.get_sep()
    orig_start = start
    orig_end = end
    # quote on all or none, to make readline completes to max prefix
    need_quotes = any(
        re.search(PATTERN_NEED_QUOTES, x) or (backslash in x and slash != backslash)
        for x in paths
    )

    for s in paths:
        start = orig_start
        end = orig_end
        if start == "" and need_quotes:
            start = end = _quote_to_use(s)
        if os.path.isdir(expand_path(s)):
            _tail = slash
        elif end == "":
            _tail = space
        else:
            _tail = ""
        if start != "" and "r" not in start and backslash in s:
            start = "r%s" % start
        s = s + _tail
        if end != "":
            if "r" not in start.lower():
                s = s.replace(backslash, double_backslash)
            if s.endswith(backslash) and not s.endswith(double_backslash):
                s += backslash
        if end in s:
            s = s.replace(end, "".join("\\%s" % i for i in end))
        s = start + s + end if append_end else start + s
        out.add(s)
    return out, need_quotes


def _joinpath(path):
    # convert our tuple representation back into a string representing a path
    if path is None:
        return ""
    elif len(path) == 0:
        return ""
    elif path == ("",):
        return xt.get_sep()
    elif path[0] == "":
        return xt.get_sep() + _normpath(os.path.join(*path))
    else:
        return _normpath(os.path.join(*path))


def _splitpath(path):
    # convert a path into an intermediate tuple representation
    # if this tuple starts with '', it means that the path was an absolute path
    path = _normpath(path)
    if path.startswith(xt.get_sep()):
        pre = ("",)
    else:
        pre = ()
    return pre + _splitpath_helper(path, ())


def _splitpath_helper(path, sofar=()):
    folder, path = os.path.split(path)
    if path:
        sofar = sofar + (path,)
    if not folder or folder == xt.get_sep():
        return sofar[::-1]
    elif xp.ON_WINDOWS and not path:
        return os.path.splitdrive(folder)[:1] + sofar[::-1]
    elif xp.ON_WINDOWS and os.path.splitdrive(path)[0]:
        return sofar[::-1]
    return _splitpath_helper(folder, sofar)


def subsequence_match(ref, typed, csc):
    """
    Detects whether typed is a subsequence of ref.

    Returns ``True`` if the characters in ``typed`` appear (in order) in
    ``ref``, regardless of exactly where in ``ref`` they occur.  If ``csc`` is
    ``False``, ignore the case of ``ref`` and ``typed``.

    Used in "subsequence" path completion (e.g., ``~/u/ro`` expands to
    ``~/lou/carcohl``)
    """
    if csc:
        return _subsequence_match_iter(ref, typed)
    else:
        return _subsequence_match_iter(ref.lower(), typed.lower())


def _subsequence_match_iter(ref, typed):
    if len(typed) == 0:
        return True
    elif len(ref) == 0:
        return False
    elif ref[0] == typed[0]:
        return _subsequence_match_iter(ref[1:], typed[1:])
    else:
        return _subsequence_match_iter(ref[1:], typed)


def _expand_one(sofar, nextone, csc):
    out = set()
    glob_sorted = builtins.__xonsh__.env.get("GLOB_SORTED")
    for i in sofar:
        _glob = os.path.join(_joinpath(i), "*") if i is not None else "*"
        for j in xt.iglobpath(_glob, sort_result=glob_sorted):
            j = os.path.basename(j)
            if subsequence_match(j, nextone, csc):
                out.add((i or ()) + (j,))
    return out


def complete_path(prefix, line, start, end, ctx, cdpath=True, filtfunc=None):
    """Completes based on a path name."""
    # string stuff for automatic quoting
    path_str_start = ""
    path_str_end = ""
    append_end = True
    p = _path_from_partial_string(line, end)
    lprefix = len(prefix)
    if p is not None:
        lprefix = len(p[0])
        prefix = p[1]
        path_str_start = p[2]
        path_str_end = p[3]
        if len(line) >= end + 1 and line[end] == path_str_end:
            append_end = False
    tilde = "~"
    paths = set()
    env = builtins.__xonsh__.env
    csc = env.get("CASE_SENSITIVE_COMPLETIONS")
    glob_sorted = env.get("GLOB_SORTED")
    prefix = glob.escape(prefix)
    for s in xt.iglobpath(prefix + "*", ignore_case=(not csc), sort_result=glob_sorted):
        paths.add(s)
    if len(paths) == 0 and env.get("SUBSEQUENCE_PATH_COMPLETION"):
        # this block implements 'subsequence' matching, similar to fish and zsh.
        # matches are based on subsequences, not substrings.
        # e.g., ~/u/ro completes to ~/lou/carcolh
        # see above functions for details.
        p = _splitpath(os.path.expanduser(prefix))
        if len(p) != 0:
            if p[0] == "":
                basedir = ("",)
                p = p[1:]
            else:
                basedir = None
            matches_so_far = {basedir}
            for i in p:
                matches_so_far = _expand_one(matches_so_far, i, csc)
            paths |= {_joinpath(i) for i in matches_so_far}
    if len(paths) == 0 and env.get("FUZZY_PATH_COMPLETION"):
        threshold = env.get("SUGGEST_THRESHOLD")
        for s in xt.iglobpath(
            os.path.dirname(prefix) + "*",
            ignore_case=(not csc),
            sort_result=glob_sorted,
        ):
            if xt.levenshtein(prefix, s, threshold) < threshold:
                paths.add(s)
    if tilde in prefix:
        home = os.path.expanduser(tilde)
        paths = {s.replace(home, tilde) for s in paths}
    if cdpath and cd_in_command(line):
        _add_cdpaths(paths, prefix)
    paths = set(filter(filtfunc, paths))
    paths, _ = _quote_paths(
        {_normpath(s) for s in paths}, path_str_start, path_str_end, append_end
    )
    paths.update(filter(filtfunc, _dots(prefix)))
    paths.update(filter(filtfunc, _env(prefix)))
    return paths, lprefix


def complete_dir(prefix, line, start, end, ctx, cdpath=False):
    return complete_path(prefix, line, start, end, cdpath, filtfunc=os.path.isdir)

#
# python
#
"""Completers for Python code"""
# amalgamated re
# amalgamated sys
inspect = _LazyModule.load('inspect', 'inspect')
# amalgamated builtins
importlib = _LazyModule.load('importlib', 'importlib')
warnings = _LazyModule.load('warnings', 'warnings')
cabc = _LazyModule.load('collections', 'collections.abc', 'cabc')
# amalgamated xonsh.tools
# amalgamated xonsh.lazyasd
# amalgamated xonsh.completers.tools
@xl.lazyobject
def RE_ATTR():
    return re.compile(r"([^\s\(\)]+(\.[^\s\(\)]+)*)\.(\w*)$")


@xl.lazyobject
def XONSH_EXPR_TOKENS():
    return {
        "and ",
        "else",
        "for ",
        "if ",
        "in ",
        "is ",
        "lambda ",
        "not ",
        "or ",
        "+",
        "-",
        "/",
        "//",
        "%",
        "**",
        "|",
        "&",
        "~",
        "^",
        ">>",
        "<<",
        "<",
        "<=",
        ">",
        ">=",
        "==",
        "!=",
        ",",
        "?",
        "??",
        "$(",
        "${",
        "$[",
        "...",
        "![",
        "!(",
        "@(",
        "@$(",
        "@",
    }


@xl.lazyobject
def XONSH_STMT_TOKENS():
    return {
        "as ",
        "assert ",
        "break",
        "class ",
        "continue",
        "def ",
        "del ",
        "elif ",
        "except ",
        "finally:",
        "from ",
        "global ",
        "import ",
        "nonlocal ",
        "pass",
        "raise ",
        "return ",
        "try:",
        "while ",
        "with ",
        "yield ",
        "-",
        "/",
        "//",
        "%",
        "**",
        "|",
        "&",
        "~",
        "^",
        ">>",
        "<<",
        "<",
        "<=",
        "->",
        "=",
        "+=",
        "-=",
        "*=",
        "/=",
        "%=",
        "**=",
        ">>=",
        "<<=",
        "&=",
        "^=",
        "|=",
        "//=",
        ";",
        ":",
        "..",
    }


@xl.lazyobject
def XONSH_TOKENS():
    return set(XONSH_EXPR_TOKENS) | set(XONSH_STMT_TOKENS)


def complete_python(prefix, line, start, end, ctx):
    """
    Completes based on the contents of the current Python environment,
    the Python built-ins, and xonsh operators.
    If there are no matches, split on common delimiters and try again.
    """
    rtn = _complete_python(prefix, line, start, end, ctx)
    if not rtn:
        prefix = (
            re.split(r"\(|=|{|\[|,", prefix)[-1]
            if not prefix.startswith(",")
            else prefix
        )
        start = line.find(prefix)
        rtn = _complete_python(prefix, line, start, end, ctx)
        return rtn, len(prefix)
    return rtn


def _complete_python(prefix, line, start, end, ctx):
    """
    Completes based on the contents of the current Python environment,
    the Python built-ins, and xonsh operators.
    """
    if line != "":
        first = line.split()[0]
        if first in builtins.__xonsh__.commands_cache and first not in ctx:
            return set()
    filt = get_filter_function()
    rtn = set()
    if ctx is not None:
        if "." in prefix:
            rtn |= attr_complete(prefix, ctx, filt)
        args = python_signature_complete(prefix, line, end, ctx, filt)
        rtn |= args
        rtn |= {s for s in ctx if filt(s, prefix)}
    else:
        args = ()
    if len(args) == 0:
        # not in a function call, so we can add non-expression tokens
        rtn |= {s for s in XONSH_TOKENS if filt(s, prefix)}
    else:
        rtn |= {s for s in XONSH_EXPR_TOKENS if filt(s, prefix)}
    rtn |= {s for s in dir(builtins) if filt(s, prefix)}
    return rtn


def complete_python_mode(prefix, line, start, end, ctx):
    """
    Python-mode completions for @( and ${
    """
    if not (prefix.startswith("@(") or prefix.startswith("${")):
        return set()
    prefix_start = prefix[:2]
    python_matches = complete_python(prefix[2:], line, start - 2, end - 2, ctx)
    if isinstance(python_matches, cabc.Sequence):
        python_matches = python_matches[0]
    return set(prefix_start + i for i in python_matches)


def _turn_off_warning(func):
    """Decorator to turn off warning temporarily."""

    def wrapper(*args, **kwargs):
        warnings.filterwarnings("ignore")
        r = func(*args, **kwargs)
        warnings.filterwarnings("once", category=DeprecationWarning)
        return r

    return wrapper


def _safe_eval(expr, ctx):
    """Safely tries to evaluate an expression. If this fails, it will return
    a (None, None) tuple.
    """
    _ctx = None
    xonsh_safe_eval = builtins.__xonsh__.execer.eval
    try:
        val = xonsh_safe_eval(expr, ctx, ctx, transform=False)
        _ctx = ctx
    except:  # pylint:disable=bare-except
        try:
            val = xonsh_safe_eval(expr, builtins.__dict__, transform=False)
            _ctx = builtins.__dict__
        except:  # pylint:disable=bare-except
            val = _ctx = None
    return val, _ctx


@_turn_off_warning
def attr_complete(prefix, ctx, filter_func):
    """Complete attributes of an object."""
    attrs = set()
    m = RE_ATTR.match(prefix)
    if m is None:
        return attrs
    expr, attr = m.group(1, 3)
    expr = xt.subexpr_from_unbalanced(expr, "(", ")")
    expr = xt.subexpr_from_unbalanced(expr, "[", "]")
    expr = xt.subexpr_from_unbalanced(expr, "{", "}")
    val, _ctx = _safe_eval(expr, ctx)
    if val is None and _ctx is None:
        return attrs
    if len(attr) == 0:
        opts = [o for o in dir(val) if not o.startswith("_")]
    else:
        opts = [o for o in dir(val) if filter_func(o, attr)]
    prelen = len(prefix)
    for opt in opts:
        # check whether these options actually work (e.g., disallow 7.imag)
        _expr = "{0}.{1}".format(expr, opt)
        _val_, _ctx_ = _safe_eval(_expr, _ctx)
        if _val_ is None and _ctx_ is None:
            continue
        a = getattr(val, opt)
        if builtins.__xonsh__.env["COMPLETIONS_BRACKETS"]:
            if callable(a):
                rpl = opt + "("
            elif isinstance(a, (cabc.Sequence, cabc.Mapping)):
                rpl = opt + "["
            else:
                rpl = opt
        else:
            rpl = opt
        # note that prefix[:prelen-len(attr)] != prefix[:-len(attr)]
        # when len(attr) == 0.
        comp = prefix[: prelen - len(attr)] + rpl
        attrs.add(comp)
    return attrs


@_turn_off_warning
def python_signature_complete(prefix, line, end, ctx, filter_func):
    """Completes a python function (or other callable) call by completing
    argument and keyword argument names.
    """
    front = line[:end]
    if xt.is_balanced(front, "(", ")"):
        return set()
    funcname = xt.subexpr_before_unbalanced(front, "(", ")")
    val, _ctx = _safe_eval(funcname, ctx)
    if val is None:
        return set()
    try:
        sig = inspect.signature(val)
    except ValueError:
        return set()
    args = {p + "=" for p in sig.parameters if filter_func(p, prefix)}
    return args


def complete_import(prefix, line, start, end, ctx):
    """
    Completes module names and contents for "import ..." and "from ... import
    ..."
    """
    ltoks = line.split()
    ntoks = len(ltoks)
    if ntoks == 2 and ltoks[0] == "from":
        # completing module to import
        return {"{} ".format(i) for i in complete_module(prefix)}
    if ntoks > 1 and ltoks[0] == "import" and start == len("import "):
        # completing module to import
        return complete_module(prefix)
    if ntoks > 2 and ltoks[0] == "from" and ltoks[2] == "import":
        # complete thing inside a module
        try:
            mod = importlib.import_module(ltoks[1])
        except ImportError:
            return set()
        out = {i[0] for i in inspect.getmembers(mod) if i[0].startswith(prefix)}
        return out
    return set()


def complete_module(prefix):
    return {s for s in sys.modules if get_filter_function()(s, prefix)}

#
# base
#
"""Base completer for xonsh."""
# amalgamated collections.abc
# amalgamated xonsh.completers.path
# amalgamated xonsh.completers.python
# amalgamated xonsh.completers.commands
def complete_base(prefix, line, start, end, ctx):
    """If the line is empty, complete based on valid commands, python names,
    and paths.  If we are completing the first argument, complete based on
    valid commands and python names.
    """
    # get and unpack python completions
    python_comps = complete_python(prefix, line, start, end, ctx)
    if isinstance(python_comps, cabc.Sequence):
        python_comps, python_comps_len = python_comps
    else:
        python_comps_len = None
    # add command completions
    out = python_comps | complete_command(prefix, line, start, end, ctx)
    # add paths, if needed
    if line.strip() == "":
        paths = complete_path(prefix, line, start, end, ctx, False)
        return (out | paths[0]), paths[1]
    elif prefix == line:
        if python_comps_len is None:
            return out
        else:
            return out, python_comps_len
    return set()

#
# bash
#
"""Xonsh hooks into bash completions."""
# amalgamated builtins
# amalgamated xonsh.platform
# amalgamated xonsh.completers.path
# amalgamated xonsh.completers.bash_completion
def complete_from_bash(prefix, line, begidx, endidx, ctx):
    """Completes based on results from BASH completion."""
    env = builtins.__xonsh__.env.detype()
    paths = builtins.__xonsh__.env.get("BASH_COMPLETIONS", ())
    command = xp.bash_command()
    return bash_completions(
        prefix,
        line,
        begidx,
        endidx,
        env=env,
        paths=paths,
        command=command,
        quote_paths=_quote_paths,
    )

#
# dirs
#
# amalgamated xonsh.completers.man
# amalgamated xonsh.completers.path
def complete_cd(prefix, line, start, end, ctx):
    """
    Completion for "cd", includes only valid directory names.
    """
    if start != 0 and line.split(" ")[0] == "cd":
        return complete_dir(prefix, line, start, end, ctx, True)
    return set()


def complete_rmdir(prefix, line, start, end, ctx):
    """
    Completion for "rmdir", includes only valid directory names.
    """
    if start != 0 and line.split(" ")[0] == "rmdir":
        opts = {
            i
            for i in complete_from_man("-", "rmdir -", 6, 7, ctx)
            if i.startswith(prefix)
        }
        comps, lp = complete_dir(prefix, line, start, end, ctx, True)
        return comps | opts, lp
    return set()

#
# init
#
"""Constructor for xonsh completer objects."""
# amalgamated collections
# amalgamated xonsh.completers.pip
# amalgamated xonsh.completers.man
# amalgamated xonsh.completers.bash
# amalgamated xonsh.completers.base
# amalgamated xonsh.completers.path
# amalgamated xonsh.completers.dirs
# amalgamated xonsh.completers.python
# amalgamated xonsh.completers.commands
# amalgamated xonsh.completers.completer
# amalgamated xonsh.completers.xompletions
def default_completers():
    """Creates a copy of the default completers."""
    return collections.OrderedDict(
        [
            ("python_mode", complete_python_mode),
            ("base", complete_base),
            ("completer", complete_completer),
            ("skip", complete_skipper),
            ("pip", complete_pip),
            ("cd", complete_cd),
            ("rmdir", complete_rmdir),
            ("xonfig", complete_xonfig),
            ("xontrib", complete_xontrib),
            ("bash", complete_from_bash),
            ("man", complete_from_man),
            ("import", complete_import),
            ("python", complete_python),
            ("path", complete_path),
        ]
    )

