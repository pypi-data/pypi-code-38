"""Amalgamation of xonsh.prompt package, made up of the following modules, in order:

* cwd
* env
* gitstatus
* job
* vc
* base

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
# cwd
#
# -*- coding: utf-8 -*-
"""CWD related prompt formatter"""

os = _LazyModule.load('os', 'os')
shutil = _LazyModule.load('shutil', 'shutil')
builtins = _LazyModule.load('builtins', 'builtins')
xt = _LazyModule.load('xonsh', 'xonsh.tools', 'xt')
xp = _LazyModule.load('xonsh', 'xonsh.platform', 'xp')
def _replace_home(x):
    if xp.ON_WINDOWS:
        home = (
            builtins.__xonsh__.env["HOMEDRIVE"] + builtins.__xonsh__.env["HOMEPATH"][0]
        )
        if x.startswith(home):
            x = x.replace(home, "~", 1)

        if builtins.__xonsh__.env.get("FORCE_POSIX_PATHS"):
            x = x.replace(os.sep, os.altsep)

        return x
    else:
        home = builtins.__xonsh__.env["HOME"]
        if x.startswith(home):
            x = x.replace(home, "~", 1)
        return x


def _replace_home_cwd():
    return _replace_home(builtins.__xonsh__.env["PWD"])


def _collapsed_pwd():
    sep = xt.get_sep()
    pwd = _replace_home_cwd().split(sep)
    l = len(pwd)
    leader = sep if l > 0 and len(pwd[0]) == 0 else ""
    base = [
        i[0] if ix != l - 1 and i[0] != "." else i[0:2] if ix != l - 1 else i
        for ix, i in enumerate(pwd)
        if len(i) > 0
    ]
    return leader + sep.join(base)


def _dynamically_collapsed_pwd():
    """Return the compact current working directory.  It respects the
    environment variable DYNAMIC_CWD_WIDTH.
    """
    original_path = _replace_home_cwd()
    target_width, units = builtins.__xonsh__.env["DYNAMIC_CWD_WIDTH"]
    elision_char = builtins.__xonsh__.env["DYNAMIC_CWD_ELISION_CHAR"]
    if target_width == float("inf"):
        return original_path
    if units == "%":
        cols, _ = shutil.get_terminal_size()
        target_width = (cols * target_width) // 100
    sep = xt.get_sep()
    pwd = original_path.split(sep)
    last = pwd.pop()
    remaining_space = target_width - len(last)
    # Reserve space for separators
    remaining_space_for_text = remaining_space - len(pwd)
    parts = []
    for i in range(len(pwd)):
        part = pwd[i]
        part_len = int(
            min(len(part), max(1, remaining_space_for_text // (len(pwd) - i)))
        )
        remaining_space_for_text -= part_len
        if len(part) > part_len:
            reduced_part = part[0 : part_len - len(elision_char)] + elision_char
            parts.append(reduced_part)
        else:
            parts.append(part)
    parts.append(last)
    full = sep.join(parts)
    truncature_char = elision_char if elision_char else "..."
    # If even if displaying one letter per dir we are too long
    if len(full) > target_width:
        # We truncate the left most part
        full = truncature_char + full[int(-target_width) + len(truncature_char) :]
        # if there is not even a single separator we still
        # want to display at least the beginning of the directory
        if full.find(sep) == -1:
            full = (truncature_char + sep + last)[
                0 : int(target_width) - len(truncature_char)
            ] + truncature_char
    return full

#
# env
#
# -*- coding: utf-8 -*-
"""Prompt formatter for virtualenv and others"""

# amalgamated os
# amalgamated builtins
# amalgamated xonsh.platform
def find_env_name():
    """Finds the current environment name from $VIRTUAL_ENV or
    $CONDA_DEFAULT_ENV if that is set.
    """
    env_path = builtins.__xonsh__.env.get("VIRTUAL_ENV", "")
    if len(env_path) == 0 and xp.ON_ANACONDA:
        env_path = builtins.__xonsh__.env.get("CONDA_DEFAULT_ENV", "")
    env_name = os.path.basename(env_path)
    return env_name


def env_name():
    """Returns the current env_name if it non-empty, surrounded by the
    ``{env_prefix}`` and ``{env_postfix}`` fields.
    """
    env_name = find_env_name()
    if builtins.__xonsh__.env.get("VIRTUAL_ENV_DISABLE_PROMPT") or not env_name:
        # env name prompt printing disabled, or no environment; just return
        return

    venv_prompt = builtins.__xonsh__.env.get("VIRTUAL_ENV_PROMPT")
    if venv_prompt is not None:
        return venv_prompt
    else:
        pf = builtins.__xonsh__.shell.prompt_formatter
        pre = pf._get_field_value("env_prefix")
        post = pf._get_field_value("env_postfix")
        return pre + env_name + post


def vte_new_tab_cwd():
    """This prints an escape sequence that tells VTE terminals the hostname
    and pwd. This should not be needed in most cases, but sometimes is for
    certain Linux terminals that do not read the PWD from the environment
    on startup. Note that this does not return a string, it simply prints
    and flushes the escape sequence to stdout directly.
    """
    env = builtins.__xonsh__.env
    t = "\033]7;file://{}{}\007"
    s = t.format(env.get("HOSTNAME"), env.get("PWD"))
    print(s, end="", flush=True)

#
# gitstatus
#
# -*- coding: utf-8 -*-
"""Informative git status prompt formatter"""

# amalgamated builtins
collections = _LazyModule.load('collections', 'collections')
# amalgamated os
subprocess = _LazyModule.load('subprocess', 'subprocess')
xl = _LazyModule.load('xonsh', 'xonsh.lazyasd', 'xl')
GitStatus = collections.namedtuple(
    "GitStatus",
    [
        "branch",
        "num_ahead",
        "num_behind",
        "untracked",
        "changed",
        "deleted",
        "conflicts",
        "staged",
        "stashed",
        "operations",
    ],
)


def _check_output(*args, **kwargs):
    kwargs.update(
        dict(
            env=builtins.__xonsh__.env.detype(),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            universal_newlines=True,
        )
    )
    timeout = builtins.__xonsh__.env["VC_BRANCH_TIMEOUT"]
    # See https://docs.python.org/3/library/subprocess.html#subprocess.Popen.communicate
    with subprocess.Popen(*args, **kwargs) as proc:
        try:
            out, err = proc.communicate(timeout=timeout)
            if proc.returncode != 0:
                raise subprocess.CalledProcessError(
                    proc.returncode, proc.args, output=out, stderr=err
                )  # note err will always be empty as we redirect stderr to DEVNULL abvoe
            return out
        except subprocess.TimeoutExpired:
            # We use `.terminate()` (SIGTERM) instead of `.kill()` (SIGKILL) here
            # because otherwise we guarantee that a `.git/index.lock` file will be
            # left over, and subsequent git operations will fail.
            # We don't want that.
            # As a result, we must rely on git to exit properly on SIGTERM.
            proc.terminate()
            # We wait() to ensure that git has finished before the next
            # `gitstatus` prompt is rendered (otherwise `index.lock` still exists,
            # and it will fail).
            # We don't technically have to call `wait()` here as the
            # `with subprocess.Popen()` context manager above would do that
            # for us, but we do it to be explicit that waiting is being done.
            proc.wait()  # we ignore what git says after we sent it SIGTERM
            raise


@xl.lazyobject
def _DEFS():
    DEFS = {
        "HASH": ":",
        "BRANCH": "{CYAN}",
        "OPERATION": "{CYAN}",
        "STAGED": "{RED}●",
        "CONFLICTS": "{RED}×",
        "CHANGED": "{BLUE}+",
        "DELETED": "{RED}-",
        "UNTRACKED": "…",
        "STASHED": "⚑",
        "CLEAN": "{BOLD_GREEN}✓",
        "AHEAD": "↑·",
        "BEHIND": "↓·",
    }
    return DEFS


def _get_def(key):
    def_ = builtins.__xonsh__.env.get("XONSH_GITSTATUS_" + key)
    return def_ if def_ is not None else _DEFS[key]


def _get_tag_or_hash():
    tag_or_hash = _check_output(["git", "describe", "--always"]).strip()
    hash_ = _check_output(["git", "rev-parse", "--short", "HEAD"]).strip()
    have_tag_name = tag_or_hash != hash_
    return tag_or_hash if have_tag_name else _get_def("HASH") + hash_


def _get_stash(gitdir):
    try:
        with open(os.path.join(gitdir, "logs/refs/stash")) as f:
            return sum(1 for _ in f)
    except IOError:
        return 0


def _gitoperation(gitdir):
    files = (
        ("rebase-merge", "REBASE"),
        ("rebase-apply", "AM/REBASE"),
        ("MERGE_HEAD", "MERGING"),
        ("CHERRY_PICK_HEAD", "CHERRY-PICKING"),
        ("REVERT_HEAD", "REVERTING"),
        ("BISECT_LOG", "BISECTING"),
    )
    return [f[1] for f in files if os.path.exists(os.path.join(gitdir, f[0]))]


def gitstatus():
    """Return namedtuple with fields:
    branch name, number of ahead commit, number of behind commit,
    untracked number, changed number, deleted number, conflicts number,
    staged number, stashed number, operation."""
    status = _check_output(["git", "status", "--porcelain", "--branch"])
    branch = ""
    num_ahead, num_behind = 0, 0
    untracked, changed, deleted, conflicts, staged = 0, 0, 0, 0, 0
    for line in status.splitlines():
        if line.startswith("##"):
            line = line[2:].strip()
            if "Initial commit on" in line:
                branch = line.split()[-1]
            elif "no branch" in line:
                branch = _get_tag_or_hash()
            elif "..." not in line:
                branch = line
            else:
                branch, rest = line.split("...")
                if " " in rest:
                    divergence = rest.split(" ", 1)[-1]
                    divergence = divergence.strip("[]")
                    for div in divergence.split(", "):
                        if "ahead" in div:
                            num_ahead = int(div[len("ahead ") :].strip())
                        elif "behind" in div:
                            num_behind = int(div[len("behind ") :].strip())
        elif line.startswith("??"):
            untracked += 1
        else:
            if len(line) > 1:
                if line[1] == "M":
                    changed += 1
                elif line[1] == "D":
                    deleted += 1
            if len(line) > 0 and line[0] == "U":
                conflicts += 1
            elif len(line) > 0 and line[0] != " ":
                staged += 1

    gitdir = _check_output(["git", "rev-parse", "--git-dir"]).strip()
    stashed = _get_stash(gitdir)
    operations = _gitoperation(gitdir)

    return GitStatus(
        branch,
        num_ahead,
        num_behind,
        untracked,
        changed,
        deleted,
        conflicts,
        staged,
        stashed,
        operations,
    )


def gitstatus_prompt():
    """Return str `BRANCH|OPERATOR|numbers`"""
    try:
        s = gitstatus()
    except subprocess.SubprocessError:
        return None

    ret = _get_def("BRANCH") + s.branch
    if s.num_ahead > 0:
        ret += _get_def("AHEAD") + str(s.num_ahead)
    if s.num_behind > 0:
        ret += _get_def("BEHIND") + str(s.num_behind)
    if s.operations:
        ret += _get_def("OPERATION") + "|" + "|".join(s.operations)
    ret += "|"
    if s.staged > 0:
        ret += _get_def("STAGED") + str(s.staged) + "{NO_COLOR}"
    if s.conflicts > 0:
        ret += _get_def("CONFLICTS") + str(s.conflicts) + "{NO_COLOR}"
    if s.changed > 0:
        ret += _get_def("CHANGED") + str(s.changed) + "{NO_COLOR}"
    if s.deleted > 0:
        ret += _get_def("DELETED") + str(s.deleted) + "{NO_COLOR}"
    if s.untracked > 0:
        ret += _get_def("UNTRACKED") + str(s.untracked) + "{NO_COLOR}"
    if s.stashed > 0:
        ret += _get_def("STASHED") + str(s.stashed) + "{NO_COLOR}"
    if s.staged + s.conflicts + s.changed + s.deleted + s.untracked + s.stashed == 0:
        ret += _get_def("CLEAN") + "{NO_COLOR}"
    ret += "{NO_COLOR}"

    return ret

#
# job
#
# -*- coding: utf-8 -*-
"""Prompt formatter for current jobs"""

xj = _LazyModule.load('xonsh', 'xonsh.jobs', 'xj')
def _current_job():
    j = xj.get_next_task()
    if j is not None:
        if not j["bg"]:
            cmd = j["cmds"][-1]
            s = cmd[0]
            if s == "sudo" and len(cmd) > 1:
                s = cmd[1]
            return s

#
# vc
#
# -*- coding: utf-8 -*-
"""Prompt formatter for simple version control branches"""
# pylint:disable=no-member, invalid-name

# amalgamated os
sys = _LazyModule.load('sys', 'sys')
queue = _LazyModule.load('queue', 'queue')
# amalgamated builtins
threading = _LazyModule.load('threading', 'threading')
# amalgamated subprocess
# amalgamated xonsh.tools
def _get_git_branch(q):
    denv = builtins.__xonsh__.env.detype()
    try:
        branches = xt.decode_bytes(
            subprocess.check_output(
                ["git", "branch"], env=denv, stderr=subprocess.DEVNULL
            )
        ).splitlines()
    except (subprocess.CalledProcessError, OSError, FileNotFoundError):
        q.put(None)
    else:
        for branch in branches:
            if not branch.startswith("* "):
                continue
            elif branch.endswith(")"):
                branch = branch.split()[-1][:-1]
            else:
                branch = branch.split()[-1]

            q.put(branch)
            break
        else:
            q.put(None)


def get_git_branch():
    """Attempts to find the current git branch. If this could not
    be determined (timeout, not in a git repo, etc.) then this returns None.
    """
    branch = None
    timeout = builtins.__xonsh__.env.get("VC_BRANCH_TIMEOUT")
    q = queue.Queue()

    t = threading.Thread(target=_get_git_branch, args=(q,))
    t.start()
    t.join(timeout=timeout)
    try:
        branch = q.get_nowait()
    except queue.Empty:
        branch = None
    return branch


def _get_hg_root(q):
    _curpwd = builtins.__xonsh__.env["PWD"]
    while True:
        if not os.path.isdir(_curpwd):
            return False
        try:
            dot_hg_is_in_curwd = any([b.name == ".hg" for b in xt.scandir(_curpwd)])
        except OSError:
            return False
        if dot_hg_is_in_curwd:
            q.put(_curpwd)
            break
        else:
            _oldpwd = _curpwd
            _curpwd = os.path.split(_curpwd)[0]
            if _oldpwd == _curpwd:
                return False


def get_hg_branch(root=None):
    """Try to get the mercurial branch of the current directory,
    return None if not in a repo or subprocess.TimeoutExpired if timed out.
    """
    env = builtins.__xonsh__.env
    timeout = env["VC_BRANCH_TIMEOUT"]
    q = queue.Queue()
    t = threading.Thread(target=_get_hg_root, args=(q,))
    t.start()
    t.join(timeout=timeout)
    try:
        root = q.get_nowait()
    except queue.Empty:
        return None
    if env.get("VC_HG_SHOW_BRANCH"):
        # get branch name
        branch_path = os.path.sep.join([root, ".hg", "branch"])
        if os.path.exists(branch_path):
            with open(branch_path, "r") as branch_file:
                branch = branch_file.read()
        else:
            branch = "default"
    else:
        branch = ""
    # add bookmark, if we can
    bookmark_path = os.path.sep.join([root, ".hg", "bookmarks.current"])
    if os.path.exists(bookmark_path):
        with open(bookmark_path, "r") as bookmark_file:
            active_bookmark = bookmark_file.read()
        if env.get("VC_HG_SHOW_BRANCH") is True:
            branch = "{0}, {1}".format(
                *(b.strip(os.linesep) for b in (branch, active_bookmark))
            )
        else:
            branch = active_bookmark.strip(os.linesep)
    else:
        branch = branch.strip(os.linesep)
    return branch


_FIRST_BRANCH_TIMEOUT = True


def _first_branch_timeout_message():
    global _FIRST_BRANCH_TIMEOUT
    sbtm = builtins.__xonsh__.env["SUPPRESS_BRANCH_TIMEOUT_MESSAGE"]
    if not _FIRST_BRANCH_TIMEOUT or sbtm:
        return
    _FIRST_BRANCH_TIMEOUT = False
    print(
        "xonsh: branch timeout: computing the branch name, color, or both "
        "timed out while formatting the prompt. You may avoid this by "
        "increasing the value of $VC_BRANCH_TIMEOUT or by removing branch "
        "fields, like {curr_branch}, from your $PROMPT. See the FAQ "
        "for more details. This message will be suppressed for the remainder "
        "of this session. To suppress this message permanently, set "
        "$SUPPRESS_BRANCH_TIMEOUT_MESSAGE = True in your xonshrc file.",
        file=sys.stderr,
    )


def current_branch():
    """Gets the branch for a current working directory. Returns an empty string
    if the cwd is not a repository.  This currently only works for git and hg
    and should be extended in the future.  If a timeout occurred, the string
    '<branch-timeout>' is returned.
    """
    branch = None
    cmds = builtins.__xonsh__.commands_cache
    # check for binary only once
    if cmds.is_empty():
        has_git = bool(cmds.locate_binary("git", ignore_alias=True))
        has_hg = bool(cmds.locate_binary("hg", ignore_alias=True))
    else:
        has_git = bool(cmds.lazy_locate_binary("git", ignore_alias=True))
        has_hg = bool(cmds.lazy_locate_binary("hg", ignore_alias=True))
    if has_git:
        branch = get_git_branch()
    if not branch and has_hg:
        branch = get_hg_branch()
    if isinstance(branch, subprocess.TimeoutExpired):
        branch = "<branch-timeout>"
        _first_branch_timeout_message()
    return branch or None


def _git_dirty_working_directory(q, include_untracked):
    status = None
    denv = builtins.__xonsh__.env.detype()
    try:
        cmd = ["git", "status", "--porcelain"]
        if include_untracked:
            cmd.append("--untracked-files=normal")
        else:
            cmd.append("--untracked-files=no")
        status = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, env=denv)
    except (subprocess.CalledProcessError, OSError, FileNotFoundError):
        q.put(None)
    if status is not None:
        return q.put(bool(status))


def git_dirty_working_directory(include_untracked=False):
    """Returns whether or not the git directory is dirty. If this could not
    be determined (timeout, file not found, etc.) then this returns None.
    """
    timeout = builtins.__xonsh__.env.get("VC_BRANCH_TIMEOUT")
    q = queue.Queue()
    t = threading.Thread(
        target=_git_dirty_working_directory, args=(q, include_untracked)
    )
    t.start()
    t.join(timeout=timeout)
    try:
        return q.get_nowait()
    except queue.Empty:
        return None


def hg_dirty_working_directory():
    """Computes whether or not the mercurial working directory is dirty or not.
    If this cannot be determined, None is returned.
    """
    env = builtins.__xonsh__.env
    cwd = env["PWD"]
    denv = env.detype()
    vcbt = env["VC_BRANCH_TIMEOUT"]
    # Override user configurations settings and aliases
    denv["HGRCPATH"] = ""
    try:
        s = subprocess.check_output(
            ["hg", "identify", "--id"],
            stderr=subprocess.PIPE,
            cwd=cwd,
            timeout=vcbt,
            universal_newlines=True,
            env=denv,
        )
        return s.strip(os.linesep).endswith("+")
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        FileNotFoundError,
    ):
        return None


def dirty_working_directory():
    """Returns a boolean as to whether there are uncommitted files in version
    control repository we are inside. If this cannot be determined, returns
    None. Currently supports git and hg.
    """
    dwd = None
    cmds = builtins.__xonsh__.commands_cache
    if cmds.lazy_locate_binary("git", ignore_alias=True):
        dwd = git_dirty_working_directory()
    if cmds.lazy_locate_binary("hg", ignore_alias=True) and dwd is None:
        dwd = hg_dirty_working_directory()
    return dwd


def branch_color():
    """Return red if the current branch is dirty, yellow if the dirtiness can
    not be determined, and green if it clean. These are bold, intense colors
    for the foreground.
    """
    dwd = dirty_working_directory()
    if dwd is None:
        color = "{BOLD_INTENSE_YELLOW}"
    elif dwd:
        color = "{BOLD_INTENSE_RED}"
    else:
        color = "{BOLD_INTENSE_GREEN}"
    return color


def branch_bg_color():
    """Return red if the current branch is dirty, yellow if the dirtiness can
    not be determined, and green if it clean. These are background colors.
    """
    dwd = dirty_working_directory()
    if dwd is None:
        color = "{BACKGROUND_YELLOW}"
    elif dwd:
        color = "{BACKGROUND_RED}"
    else:
        color = "{BACKGROUND_GREEN}"
    return color

#
# base
#
# -*- coding: utf-8 -*-
"""Base prompt, provides PROMPT_FIELDS and prompt related functions"""

# amalgamated builtins
itertools = _LazyModule.load('itertools', 'itertools')
# amalgamated os
re = _LazyModule.load('re', 're')
socket = _LazyModule.load('socket', 'socket')
# amalgamated sys
# amalgamated xonsh.lazyasd
# amalgamated xonsh.tools
# amalgamated xonsh.platform
# amalgamated xonsh.prompt.cwd
# amalgamated xonsh.prompt.job
# amalgamated xonsh.prompt.env
# amalgamated xonsh.prompt.vc
# amalgamated xonsh.prompt.gitstatus
@xt.lazyobject
def DEFAULT_PROMPT():
    return default_prompt()


class PromptFormatter:
    """Class that holds all the related prompt formatting methods,
    uses the ``PROMPT_FIELDS`` envvar (no color formatting).
    """

    def __init__(self):
        self.cache = {}

    def __call__(self, template=DEFAULT_PROMPT, fields=None):
        """Formats a xonsh prompt template string."""
        if fields is None:
            self.fields = builtins.__xonsh__.env.get("PROMPT_FIELDS", PROMPT_FIELDS)
        else:
            self.fields = fields
        try:
            prompt = self._format_prompt(template=template)
        except Exception:
            return _failover_template_format(template)
        # keep cache only during building prompt
        self.cache.clear()
        return prompt

    def _format_prompt(self, template=DEFAULT_PROMPT):
        template = template() if callable(template) else template
        toks = []
        for literal, field, spec, conv in xt.FORMATTER.parse(template):
            toks.append(literal)
            entry = self._format_field(field, spec, conv)
            if entry is not None:
                toks.append(entry)
        return "".join(toks)

    def _format_field(self, field, spec, conv):
        if field is None:
            return
        elif field.startswith("$"):
            val = builtins.__xonsh__.env[field[1:]]
            return _format_value(val, spec, conv)
        elif field in self.fields:
            val = self._get_field_value(field)
            return _format_value(val, spec, conv)
        else:
            # color or unknown field, return as is
            return "{" + field + "}"

    def _get_field_value(self, field):
        field_value = self.fields[field]
        if field_value in self.cache:
            return self.cache[field_value]
        try:
            value = field_value() if callable(field_value) else field_value
            self.cache[field_value] = value
        except Exception:
            print("prompt: error: on field {!r}" "".format(field), file=sys.stderr)
            xt.print_exception()
            value = "{{BACKGROUND_RED}}{{ERROR:{}}}{{NO_COLOR}}".format(field)
        return value


@xl.lazyobject
def PROMPT_FIELDS():
    return dict(
        user=xp.os_environ.get("USERNAME" if xp.ON_WINDOWS else "USER", "<user>"),
        prompt_end="#" if xt.is_superuser() else "$",
        hostname=socket.gethostname().split(".", 1)[0],
        cwd=_dynamically_collapsed_pwd,
        cwd_dir=lambda: os.path.dirname(_replace_home_cwd()),
        cwd_base=lambda: os.path.basename(_replace_home_cwd()),
        short_cwd=_collapsed_pwd,
        curr_branch=current_branch,
        branch_color=branch_color,
        branch_bg_color=branch_bg_color,
        current_job=_current_job,
        env_name=env_name,
        env_prefix="(",
        env_postfix=") ",
        vte_new_tab_cwd=vte_new_tab_cwd,
        gitstatus=gitstatus_prompt,
    )


def default_prompt():
    """Creates a new instance of the default prompt."""
    if xp.ON_CYGWIN or xp.ON_MSYS:
        dp = (
            "{env_name}"
            "{BOLD_GREEN}{user}@{hostname}"
            "{BOLD_BLUE} {cwd} {prompt_end}{NO_COLOR} "
        )
    elif xp.ON_WINDOWS and not xp.win_ansi_support():
        dp = (
            "{env_name}"
            "{BOLD_INTENSE_GREEN}{user}@{hostname}{BOLD_INTENSE_CYAN} "
            "{cwd}{branch_color}{curr_branch: {}}{NO_COLOR} "
            "{BOLD_INTENSE_CYAN}{prompt_end}{NO_COLOR} "
        )
    else:
        dp = (
            "{env_name}"
            "{BOLD_GREEN}{user}@{hostname}{BOLD_BLUE} "
            "{cwd}{branch_color}{curr_branch: {}}{NO_COLOR} "
            "{BOLD_BLUE}{prompt_end}{NO_COLOR} "
        )
    return dp


def _failover_template_format(template):
    if callable(template):
        try:
            # Exceptions raises from function of producing $PROMPT
            # in user's xonshrc should not crash xonsh
            return template()
        except Exception:
            xt.print_exception()
            return "$ "
    return template


@xt.lazyobject
def RE_HIDDEN():
    return re.compile("\001.*?\002")


def multiline_prompt(curr=""):
    """Returns the filler text for the prompt in multiline scenarios."""
    line = curr.rsplit("\n", 1)[1] if "\n" in curr else curr
    line = RE_HIDDEN.sub("", line)  # gets rid of colors
    # most prompts end in whitespace, head is the part before that.
    head = line.rstrip()
    headlen = len(head)
    # tail is the trailing whitespace
    tail = line if headlen == 0 else line.rsplit(head[-1], 1)[1]
    # now to construct the actual string
    dots = builtins.__xonsh__.env.get("MULTILINE_PROMPT")
    dots = dots() if callable(dots) else dots
    if dots is None or len(dots) == 0:
        return ""
    tokstr = xt.format_color(dots, hide=True)
    baselen = 0
    basetoks = []
    for x in tokstr.split("\001"):
        pre, sep, post = x.partition("\002")
        if len(sep) == 0:
            basetoks.append(("", pre))
            baselen += len(pre)
        else:
            basetoks.append(("\001" + pre + "\002", post))
            baselen += len(post)
    if baselen == 0:
        return xt.format_color("{NO_COLOR}" + tail, hide=True)
    toks = basetoks * (headlen // baselen)
    n = headlen % baselen
    count = 0
    for tok in basetoks:
        slen = len(tok[1])
        newcount = slen + count
        if slen == 0:
            continue
        elif newcount <= n:
            toks.append(tok)
        else:
            toks.append((tok[0], tok[1][: n - count]))
        count = newcount
        if n <= count:
            break
    toks.append((xt.format_color("{NO_COLOR}", hide=True), tail))
    rtn = "".join(itertools.chain.from_iterable(toks))
    return rtn


def is_template_string(template, PROMPT_FIELDS=None):
    """Returns whether or not the string is a valid template."""
    template = template() if callable(template) else template
    try:
        included_names = set(i[1] for i in xt.FORMATTER.parse(template))
    except ValueError:
        return False
    included_names.discard(None)
    if PROMPT_FIELDS is None:
        fmtter = builtins.__xonsh__.env.get("PROMPT_FIELDS", PROMPT_FIELDS)
    else:
        fmtter = PROMPT_FIELDS
    known_names = set(fmtter.keys())
    return included_names <= known_names


def _format_value(val, spec, conv):
    """Formats a value from a template string {val!conv:spec}. The spec is
    applied as a format string itself, but if the value is None, the result
    will be empty. The purpose of this is to allow optional parts in a
    prompt string. For example, if the prompt contains '{current_job:{} | }',
    and 'current_job' returns 'sleep', the result is 'sleep | ', and if
    'current_job' returns None, the result is ''.
    """
    if val is None:
        return ""
    val = xt.FORMATTER.convert_field(val, conv)
    if spec:
        val = xt.FORMATTER.format(spec, val)
    if not isinstance(val, str):
        val = str(val)
    return val

