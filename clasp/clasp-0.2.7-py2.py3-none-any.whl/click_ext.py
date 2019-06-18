# Copyright (c) 2018 Stephen Wasilewski
# =======================================================================
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# =======================================================================

"""extension, callbacks and interface for parsing with click and configparse"""

from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import zip
import click
import configparser
import re
import tempfile
import sys
import os
import shlex
import collections
import traceback
from glob import glob

import clasp.script_tools as mgr


# Edited from click completion script to avoid running out of turn (faster)
COMPLETION_SCRIPT_BASH = '''
%(complete_func)s() {
    local cw="${COMP_WORDS[*]}"
    if [[ $cw != *">"* ]]; then
    if [[ ${COMP_WORDS[$COMP_CWORD]} != -* ]] && [[ ${COMP_WORDS[$COMP_CWORD-1]} == -* ]]; then
        :
    else
        local IFS=$'\n'
        COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \\
                    COMP_CWORD=$COMP_CWORD \\
                    %(autocomplete_var)s=complete $1 ) )
    fi
    fi
    return 0
}

%(complete_func)setup() {
    local COMPLETION_OPTIONS=""
    local BASH_VERSION_ARR=(${BASH_VERSION//./ })
    # Only BASH version 4.4 and later have the nosort option.
    if [ ${BASH_VERSION_ARR[0]} -gt 4 ] || ([ ${BASH_VERSION_ARR[0]} -eq 4'''\
''' ] && [ ${BASH_VERSION_ARR[1]} -ge 4 ]); then
        COMPLETION_OPTIONS="-o nosort"
    fi

    complete $COMPLETION_OPTIONS -o default -F %(complete_func)s '''\
'''%(script_names)s
}

%(complete_func)setup
'''

# basic script template for one offs, docstring contains available callback
# descriptions
script_template = '''#!/usr/bin/env python
from __future__ import print_function

from clasp import click
import clasp.click_ext as clk

@click.command()
@click.argument('arg1')
@click.option('--opts','-opts', is_flag=True,
              help="check parsed options")
@click.option('--debug/--no-debug', default=True,
              help="show traceback on exceptions")
@click.pass_context
def main(ctx, arg1, **kwargs):
    """
    callbacks:

    File input
    ~~~~~~~~~~

    file inputs can be given with wildcard expansion (in quotes so that the callback handles)
    using glob plus the following:

        * [abc] (one of a, b, or c) 
        * [!abc] (none of a, b or c)
        * '-' (hyphen) collect the stdin into a temporary file (clasp_tmp*)
        * ~ expands user

    The file input callbacks are:

        * parse_file_list: returns list of files (raise error if file not found)
        * is_file: check if a single path exists (prompts for user input if file not found)
        * are_files: recursively calls parse_file_list and prompts on error
        * is_file_iter: use when multiple=True
        * are_files_iter: use when mulitple=True
        * are_files_or_str: tries to parse as files, then tries split_float, then split_int, then returns string
        * are_files_or_str_iter: use when mulitple=True

    String parsing
    ~~~~~~~~~~~~~~

        * split_str: split with shlex.split
        * split_str_iter: use when multiple=True
        * color_inp: return alphastring, split on whitespace, convert floats and parse tuples on ,

    Number parsing
    ~~~~~~~~~~~~~~

        * tup_int: parses integer tuples from comma/space seperated string
        * tup_float: parses float tuples from comma/space seperated string
        * split_float: splits list of floats and extends ranges based on : notation
        * split_int: splits list of ints and extends ranges based on : notation
    """
    if kwargs['opts']:
        kwargs['opts'] = False
        clk.echo_args(arg1, **kwargs)
    else:
        try:
            pass
        except click.Abort:
            raise
        except Exception as ex:
            clk.print_except(ex, kwargs['debug'])
    try:
        clk.tmp_clean(ctx)
    except Exception:
        pass

if __name__ == '__main__':
    main()'''


script_template2 = '''#!/usr/bin/env python
from __future__ import print_function

from clasp import click
import clasp.click_ext as clk

@click.group()
@clk.shared_decs(clk.main_decs)
def main(ctx, config, outconfig, configalias, inputalias):
    """help configuration and process management commands."""
    clk.get_config(ctx, config, outconfig, configalias, inputalias)


@main.command()
@click.argument('arg1')
@click.option('--opts','-opts', is_flag=True,
              help="check parsed options")
@click.option('--debug/--no-debug', default=True,
              help="show traceback on exceptions")
@click.pass_context
def XXX(ctx, arg1, **kwargs):
    """
    callbacks:

    File input
    ~~~~~~~~~~

    file inputs can be given with wildcard expansion (in quotes so that the callback handles)
    using glob plus the following:

        * [abc] (one of a, b, or c) 
        * [!abc] (none of a, b or c)
        * '-' (hyphen) collect the stdin into a temporary file (clasp_tmp*)
        * ~ expands user

    The file input callbacks are:

        * parse_file_list: returns list of files (raise error if file not found)
        * is_file: check if a single path exists (prompts for user input if file not found)
        * are_files: recursively calls parse_file_list and prompts on error
        * is_file_iter: use when multiple=True
        * are_files_iter: use when mulitple=True
        * are_files_or_str: tries to parse as files, then tries split_float, then split_int, then returns string
        * are_files_or_str_iter: use when mulitple=True

    String parsing
    ~~~~~~~~~~~~~~

        * split_str: split with shlex.split
        * split_str_iter: use when multiple=True
        * color_inp: return alphastring, split on whitespace, convert floats and parse tuples on ,

    Number parsing
    ~~~~~~~~~~~~~~

        * tup_int: parses integer tuples from comma/space seperated string
        * tup_float: parses float tuples from comma/space seperated string
        * split_float: splits list of floats and extends ranges based on : notation
        * split_int: splits list of ints and extends ranges based on : notation
    """
    if kwargs['opts']:
        kwargs['opts'] = False
        clk.echo_args(arg1, **kwargs)
    else:
        try:
            pass
        except click.Abort:
            raise
        except Exception as ex:
            clk.print_except(ex, kwargs['debug'])
    return 'XXX', kwargs, ctx


@main.resultcallback()
@click.pass_context
def printconfig(ctx, opts, **kwargs):
    """callback to save config file"""
    try:
        clk.tmp_clean(opts[2])
    except Exception:
        pass
    if kwargs['outconfig']:
        clk.print_config(ctx, opts, kwargs['outconfig'], kwargs['config'],
                         kwargs['configalias'])


if __name__ == '__main__':
    main()'''


def click_ext(click):
    '''customize click help messages and bash complete'''
    orig_init = click.core.Option.__init__

    def new_init(self, *args, **kwargs):
        orig_init(self, *args, **kwargs)
        if 'show_default' not in kwargs:
            self.show_default = True

    def format_help_text(self, ctx, formatter):
        """modified help text formatter for compatibility with sphinx-click."""
        if self.help:
            formatter.write_paragraph()
            with formatter.indentation():
                indent = ' ' * formatter.current_indent
                formatter.write(indent +
                                self.help.replace("\n", "\n{}".format(indent)))
            formatter.write_paragraph()

    def format_options(self, ctx, formatter):
        """Writes all the options into the formatter if they exist."""
        opts = []
        for param in self.get_params(ctx):
            rv = param.get_help_record(ctx)
            if rv is not None:
                a, name, _ = index_param(ctx, param)
                opts.append((a, name, rv))
        seps = [(i[0], ("\n" + i[1] + "\n", '')) for i in index_seps(opts)]
        opts = [i[-1] for i in sorted(opts + seps, key=lambda x: (x[0], x[1]))]
        if opts:
            with formatter.section('Options'):
                formatter.write_dl(opts)
    click.core.Option.__init__ = new_init
    click.core.Command.format_help_text = format_help_text
    click.core.Command.format_options = format_options

    import click._bashcomplete as _bc

    def get_completion_script(prog_name, complete_var, shell):
        cf_name = _bc._invalid_ident_char_re.sub('',
                                                 prog_name.replace('-', '_'))
        if shell == 'zsh':
            script = _bc.COMPLETION_SCRIPT_ZSH
        else:
            script = COMPLETION_SCRIPT_BASH
        return (script % {
            'complete_func': '_%s_completion' % cf_name,
            'script_names': prog_name,
            'autocomplete_var': complete_var,
        }).strip() + ';'

    def bashcomplete(cli, prog_name, complete_var, complete_instr):
        if complete_instr.startswith('source'):
            shell = 'zsh' if complete_instr == 'source_zsh' else 'bash'
            click.echo(get_completion_script(prog_name, complete_var, shell))
            return True
        elif complete_instr == 'complete' or complete_instr == 'complete_zsh':
            return _bc.do_complete(cli, prog_name,
                                   complete_instr == 'complete_zsh')
        return False

    def _bashcomplete(cmd, prog_name, complete_var=None):
        """Internal handler for the bash completion support."""
        if complete_var is None:
            complete_var = '_%s_COMPLETE' % (prog_name.replace('-', '_'))
            complete_var = complete_var.upper()
        complete_instr = os.environ.get(complete_var)
        if not complete_instr:
            return
        if bashcomplete(cmd, prog_name, complete_var, complete_instr):
            click.core.fast_exit(1)

    click.core._bashcomplete = _bashcomplete
    click._bashcomplete.COMPLETION_SCRIPT_BASH = COMPLETION_SCRIPT_BASH
    return click


# shared decorators for all main command groups
def main_decs(v):
    md = [
        click.option('--config', '-c', type=click.Path(exists=True)),
        click.option('--outconfig', '-oc', type=click.Path(file_okay=True)),
        click.option('--configalias', '-ca',
                     help="store config in alias section. use to store multiple"
                     "settings for same command"),
        click.option('--inputalias/--no-inputalias', default=True,
                     help="if true uses -ca for loading settings"),
        click.version_option(version=v),
        click.pass_context
    ]
    return md


def shared_decs(decs):
    '''decorator to add decs to function'''
    def decorate(f):
        for dec in reversed(decs):
            f = dec(f)
        return f
    return decorate


def callback_error(s, param, example):
    """standard error message for exceptions raised during argument parsing

    used by custom callback functions raises ClickException

    Parameters
    ----------
    s: value
    param: click.core.Option
    example: example of valid entry format
    """
    message = "\ncan't parse: {}\nexpected input "\
              "format: '{}'".format(s, example)
    raise click.BadParameter(message)


def expandpat(pat, s, mark=0):
    '''expand sglob pattern for each character option'''
    if re.search(pat, s):
        parts = re.split(pat, s)
        marks = re.findall(pat, s)
        patm = []
        for i, ma in enumerate(marks):
            part = [parts[i]] * (len(ma) - (2 + mark))
            for j, mai in enumerate(ma[1 + mark:-1]):
                part[j] += mai
            patm.append(part)
        patm.append([parts[-1]])
        allpat = [''.join(i) for i in zip(*mgr.crossref_all(patm))]
        return allpat
    else:
        return []


def sglob(s):
    '''super glob includes [abc] notation + [!abc] exclude notation'''
    inre = '\[[\w\d\-\_\.]+\]'
    exre = '\[\![\w\d\-\_\.]+\]'
    inpat = expandpat(inre, s) + [s]
    exglob = mgr.flat_list([expandpat(exre, i, 1) for i in inpat])
    inglob = [re.sub(exre, '*', i) for i in inpat]
    infiles = set(mgr.flat_list([glob(i) for i in inglob]))
    exfiles = set(mgr.flat_list([glob(i) for i in exglob]))
    return sorted(list(infiles.difference(exfiles)))


def tmp_stdin(ctx):
    '''read stdin into temporary file'''
    if not ctx.resilient_parsing:
        f, path = tempfile.mkstemp(dir="./", prefix='clasp_tmp')
        f = open(path, 'w')
        f.write(sys.stdin.read())
        f.close()
        if ctx.obj is None:
            ctx.obj = dict(temps=[path])
        else:
            ctx.obj['temps'].append(path)
        return path
    else:
        return "-"


def tmp_clean(ctx):
    '''reomve files placed int temps context object
    (called at end of scripts)'''
    for i in ctx.obj['temps']:
        try:
            os.remove(i)
        except Exception:
            pass


def parse_file_list(ctx, s):
    """parses list of files using glob expansion"""
    files = []
    for i in shlex.split(s):
        if "~" in i:
            i = os.path.expanduser(i)
        if i == '-':
            files.append(tmp_stdin(ctx))
        elif i[0] == '@':
            if os.path.exists(i[1:]):
                f = open(i[1:],'r')
                fi = [j.strip() for j in f.readlines()]
                for l in fi:
                    files += parse_file_list(ctx, l)
            else:
                raise ValueError(i[1:])
        elif len(sglob(i)) > 0:
            for j in sglob(i):
                if os.path.exists(j):
                    files.append(j)
                else:
                    raise ValueError(j)
        else:
            if os.path.exists(i):
                files.append(i)
            else:
                raise ValueError(i)
    return files


def is_file(ctx, param, s):
    """checks input file string with recursive prompt"""
    if s == '-':
        return tmp_stdin(ctx)
    if s is None:
        return None
    command = ctx.info_name
    name = param.name
    try:
        if os.path.exists(s):
            return s
        else:
            raise ValueError(s)
    except ValueError as e:
        try:
            # use os.environ['CLASP_PIPE'] = '1' in parent script
            # or set CLASP_PIPE=1
            # to disable prompt and avoid hanging process
            nopipe = os.environ['CLASP_PIPE'] != '1'
        except KeyError:
            nopipe = True
        click.echo("{} not an existing file".format(e), err=True)
        if nopipe and not ctx.resilient_parsing:
            s2 = click.prompt("{} for {}".format(name, command))
            return is_file(ctx, param, s2)
        else:
            raise click.Abort()


def are_files(ctx, param, s, prompt=True):
    """checks input file list string with recursive prompt"""
    if s is None:
        return None
    command = ctx.info_name
    name = param.name
    try:
        return parse_file_list(ctx, s)
    except ValueError as e:
        if prompt and not ctx.resilient_parsing:
            try:
                # use os.environ['CLASP_PIPE'] = '1' in parent script
                # or set CLASP_PIPE=1
                # to disable prompt
                nopipe = os.environ['CLASP_PIPE'] != '1'
            except KeyError:
                nopipe = True
            click.echo("{} not an existing file".format(e), err=True)
            if nopipe and ctx.resilient_parsing:
                s2 = click.prompt("{} for {}".format(name, command))
            else:
                raise click.Abort()
        else:
            raise ValueError(e)
        return are_files(ctx, param, s2)


def is_files_iter(ctx, param, s):
    """calls are_files for each item in iterable s"""
    files = []
    for s2 in s:
        files.append(is_file(ctx, param, s2))
    return files


def are_files_iter(ctx, param, s, prompt=True):
    """calls are_files for each item in iterable s"""
    files = []
    for s2 in s:
        files.append(are_files(ctx, param, s2, prompt))
    return files


def are_files_or_str(ctx, param, s):
    """tries are_files for each item then split_str"""
    try:
        return are_files(ctx, param, s, False)
    except ValueError:
        pass
    try:
        return [str(i) for i in split_int(ctx, param, s)]
    except Exception:
        pass
    try:
        return [str(i) for i in split_float(ctx, param, s)]
    except Exception:
        pass
    return split_str(ctx, param, s)


def are_files_or_str_iter(ctx, param, s):
    """tries are_files then split_str"""
    files = []
    for s2 in s:
        files.append(are_files_or_str(ctx, param, s2))
    return files


def split_str_iter(ctx, param, s):
    """calls are_files for each item in iterable s"""
    args = []
    for s2 in s:
        args.append(split_str(ctx, param, s2))
    return args


def color_inp(ctx, param, s):
    """parses color tuple from comma/space seperated string or cmap name"""
    if re.match("^([\d\.]+[, \t]+)+[\d\.]+$", s):
        so = []
        for x in s.split():
            if "," in x:
                so.append(tuple(float(i) for i in x.split(",")))
            else:
                so.append(float(x))
        return so
    else:
        return s


def int_rng(s):
    result = []
    for part in s.split():
        if ':' in part:
            a = (int(i) for i in part.split(':'))
            result.extend(mgr.arange(*a))
        else:
            a = int(part)
            result.append(a)
    if len(result) == 1:
        result = [int(result[0])]
    return result


def tup_int(ctx, param, s):
    """parses integer tuples from comma/space seperated string"""
    if s is None:
        so = None
    else:
        try:
            so = []
            for x in s.split():
                if "," in x:
                    for fis in int_rng(x.split(",")[0]):
                        for col in int_rng(x.split(",")[1]):
                            so.append((fis, col))
                else:
                    so.extend(int_rng(x))
        except Exception:
            callback_error(s, param, '0 0,1 0,3')
    return so


def tup_float(ctx, param, s):
    """parses float tuples from comma/space seperated string"""
    if s is None:
        so = None
    else:
        try:
            so = []
            for x in s.split():
                if "," in x:
                    so.append(tuple(float(i) for i in x.split(",")))
                else:
                    so.append(float(x))
        except Exception:
            callback_error(s, param, '0 0,1 0,3.6')
    return so


def split_str(ctx, param, s):
    """splits space seperated string"""
    if s is None:
        return None
    elif s[0] == '@':
        if os.path.exists(s[1:]):
            f = open(s[1:],'r')
            return shlex.split(f.read().strip())
        else:
            return shlex.split(s)
    else:
        return shlex.split(s)


def tup_list(ctx, param, s):
    """convert tuple to list"""
    if s is not None:
        return list(s)
    else:
        return None


def split_float(ctx, param, s):
    """splits list of floats and extends ranges based on : notation"""
    if s is None:
        result = None
    else:
        try:
            result = []
            for part in s.split():
                if ':' in part:
                    a = (float(i) for i in part.split(':'))
                    result.extend(mgr.arange(*a))
                else:
                    a = float(part)
                    result.append(a)
            result = [round(i, 6) for i in result]
        except Exception:
            callback_error(s, param, '0 30.5 40')
    return result


def split_int(ctx, param, s):
    """splits list of ints and extends ranges based on : notation"""
    if s is None:
        result = None
    else:
        try:
            result = []
            for part in s.split():
                if ':' in part:
                    a = (int(i) for i in part.split(':'))
                    result.extend(mgr.arange(*a))
                else:
                    a = int(part)
                    result.append(a)
            if len(result) == 1:
                result = [int(result[0])]
        except Exception:
            callback_error(s, param, '0 30 40')
    return result


def ConfigSectionMap(Config, section):
    """maps ConfigParser section to dict"""
    dict1 = {}
    options = Config.options(section)
    try:
        cvars = Config.options('globals')
    except Exception:
        cvars = []
    for cvar in cvars:
        Config.set(section, cvar, Config.get('globals', cvar))
    for option in options:
        try:
            opt = Config.get(section, option)
            if re.match('.+_\d+', option):
                opto = option.rsplit("_", 1)[0]
                try:
                    dict1[opto].append(opt)
                except Exception:
                    dict1[opto] = [opt]
            elif opt == "None":
                dict1[option] = None
            else:
                dict1[option] = opt
        except Exception as ex:
            click.echo("exception on {}! {}".format(option, ex), err=True)
            dict1[option] = None
    return dict1


def format_depth(v):
    '''recursively format lists and tuples'''
    if type(v) == list:
        wv = " ".join([format_depth(i) for i in v])
    elif type(v) == tuple:
        wv = ",".join([format_depth(i) for i in v])
    else:
        wv = str(v)
    return wv


def formatarg(Parser, command, name, v):
    """formats option to write to config file"""
    try:
        v = v.name
    except AttributeError:
        pass
    wv = format_depth(v)
    try:
        Parser.set(command, name, wv)
    except configparser.NoSectionError:
        Parser.add_section(command)
        Parser.set(command, name, wv)
    return Parser


def setargs(Config, ini, section):
    """gets command section from .ini file"""
    try:
        Config.read(ini)
        return ConfigSectionMap(Config, section)
    except Exception:
        return {}


def index_param(ctx, param):
    '''tag param with index to sort by option type for help display'''
    if param.human_readable_name == 'help':
        a = 10
    elif param.human_readable_name == 'debug':
        a = 9
    elif param.human_readable_name == 'opts':
        a = 8
    elif param.required:
        a = 1
    elif param.prompt:
        a = 2
    elif param.is_flag:
        if param.get_default(ctx):
            a = 4
        else:
            a = 5
    else:
        a = 3
    return a, param.human_readable_name, param


def index_seps(params):
    '''insert section headers into param list for help display'''
    seps = []
    sections = set([i[0] for i in params])
    if 1 in sections:
        seps.append((0.5, "REQUIRED:"))
    if 2 in sections:
        seps.append((1.5, "HAS PROMPT:"))
    if 3 in sections:
        seps.append((2.5, "VALUE OPTIONS:"))
    if 4 in sections:
        seps.append((3.5, "FLAGS (DEFAULT TRUE):"))
    if 5 in sections:
        seps.append((4.5, "FLAGS (DEFAULT FALSE):"))
    if [i for i in [8, 9, 10] if i in sections]:
        seps.append((7.5, 'HELP:'))
    return seps


def get_config(ctx, config, outconfig, configalias, inputalias, template=None):
    """load config file into click options"""
    Parser = configparser.ConfigParser()
    com = ctx.info_name.split("_")[-1]
    subc = ctx.invoked_subcommand
    if configalias and template is not None:
        gargs = setargs(Parser, template, "{}_{}".format(com, configalias))
    else:
        gargs = {}
    if configalias is not None and inputalias:
        alias = "{}_{}".format(com, configalias)
        args = setargs(Parser, config, alias)
    else:
        alias = "{}_{}".format(com, subc)
        args = setargs(Parser, config, alias)
    gargs.update(args)
    if not gargs and outconfig is None and (config is not None or configalias):
        click.echo("WARNING: {} not found in local config file: {} or "
                   "global config file: {}"
                   "".format(alias, config, template), err=True)
        raise click.Abort()
    ctx.command.commands[subc].context_settings['default_map'] = gargs


def match_multiple(ctx, subc):
    '''identify params with multiple=True for config file parsing'''
    ismultiple = {}
    for opt in ctx.command.commands[subc].params:
        ismultiple[opt.human_readable_name] = opt.multiple
    return ismultiple


def config_comments(*args):
    '''read in comments from config files'''
    comments = ['# Usage:']
    for arg in args:
        try:
            f = open(arg, 'r')
        except Exception:
            pass
        else:
            cm = [i.strip() for i in f.readlines()
                  if re.match("^#", i.strip())]
            f.close()
            for c in cm:
                if c not in comments:
                    comments.append(c)
    return("\n".join(comments) + "\n\n")


def add_opt_comment(comments, opts):
    '''add comment lines for opts unless present'''
    comments = comments.strip()
    for opt in opts:
        if not re.search(r'#\s*\[{}\]'.format(opt), comments):
            comments += "{: <30}#".format('\n# [{}]'.format(opt))
    return comments + "\n\n"


def print_config(ctx, opts, outconfig, config, configalias):
    """write config file from click options"""
    ismultiple = match_multiple(ctx, opts[0])
    com = ctx.info_name.split("_")[-1]
    if configalias is not None:
        opt = "{}_{}".format(com, configalias)
    else:
        opt = "{}_{}".format(com, opts[0])
    Parser = configparser.ConfigParser()
    try:
        Parser.read(config)
    except Exception:
        pass
    try:
        Parser.read(outconfig)
    except Exception:
        pass
    comments = config_comments(config, outconfig)
    for i, v in list(opts[1].items()):
        try:
            if ismultiple[i]:
                for j, k in enumerate(v):
                    subo = "{}_{:03d}".format(i, j)
                    Parser = formatarg(Parser, opt, subo, k)
            else:
                Parser = formatarg(Parser, opt, i, v)
        except KeyError:
            pass
    comments = add_opt_comment(comments, Parser.sections())
    for s in Parser._sections:
        srt = sorted(list(Parser._sections[s].items()), key=lambda t: t[0])
        Parser._sections[s] = collections.OrderedDict(srt)
    f = open(outconfig, 'w')
    f.write(comments)
    Parser.write(f)
    f.close()


def print_except(ex, debug=False):
    '''general human readable exception message'''
    if debug:
        traceback.print_exc()
    click.echo("\n**************\n**************", err=True)
    click.echo("Execution failed:", err=True)
    click.echo("{}: {}".format(type(ex).__name__, ex), err=True)
    click.echo("**************\n**************\n", err=True)


def formatarg_line(v, i=None, idx=None):
    '''reduce output of long lists subroutine'''
    if len(v) > 30 or len("".join(["{}".format(j) for j in v])) > 100:
        sv = ""
        k = 0
        while (len(sv) <= 30 and k < 10) or k < 3:
            sv += "{}, ".format(v[k])
            k += 1
        a = "list of length: {} [ {}... , {} ]".format(len(v), sv, v[-1])
    else:
        a = "{}".format(v)
    if i is not None:
        if idx is not None:
            i = "{}_{:03d}".format(i, idx)
        a = "{0:.<15}{1}".format(i, a)
    return a


def formatarg_stdout(v, i=None):
    '''reduce output of long lists'''
    if type(v) == tuple or type(v) == list:
        if len(v) > 0 and type(v[0]) == list:
            a = []
            for j, v0 in enumerate(v):
                a += [formatarg_line(v0, i=i, idx=j)]
            a = "\n".join(a)
        else:
            a = formatarg_line(v, i)
    else:
        a = "{}".format(v)
        if i is not None:
            a = "{0:.<15}{1}".format(i, a)
    return a


def echo_args(*args, **kwargs):
    """print human readable version of parsed args"""
    print("Positonal Arguments:\n", file=sys.stderr)
    for v in args:
        try:
            v.tell()
        except AttributeError:
            pass
        else:
            try:
                v = v.name
            except Exception:
                v = "file like object"
        print(formatarg_stdout(v), file=sys.stderr)
    print("\nOptions:\n", file=sys.stderr)
    srt = sorted([(i, u) for i, u in list(kwargs.items())])
    for i, v in srt:
        print(formatarg_stdout(v, i), file=sys.stderr)
