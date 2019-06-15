import os
import re
import shlex
import subprocess

from collections import ChainMap
from collections.abc import Mapping
from pathlib import Path

DOTENV_DEFAULT_FILE = '.env'
DOTENV_VAR_NAME = re.compile(r"[A-Za-z]+[A-Za-z0-9_]*")
DOTENV_SUPPORTED_COMMANDS = ('export', 'source')
DOTENV_VAR_SUBS = re.compile(r"(\${\s*([A-Za-z]+[A-Za-z0-9_]*)\s*\})")
DOTENV_BREAK_SIGNS = [';', '&', '\n', ' ']


class DotEnvException(Exception):
    pass


class DotEnvParserError(DotEnvException):
    pass


class DotEnvNotAllowed(DotEnvException):
    pass


def organize_tokens(tokens, rest=None):
    rest = rest or list()

    # Detect first in-text line break
    break_point = next((i for i, token in enumerate(tokens) if token in DOTENV_BREAK_SIGNS), None)

    # Got a break point: split the line into the first valid sequence and the rest
    if break_point is not None:
        return [*rest, *tokens[0:break_point]], tokens[break_point+1:]

    return [*rest, *tokens], []


def parse_row(row, rest=None):
    rest = rest or list()

    # If row is empty, there is nothing to do
    if not row:
        return rest, list()

    # Presumes non-empty rows from here onwards
    # shlex will address quotes and comments for us
    lex = shlex.shlex(row, posix=True, punctuation_chars=False)
    tokens = list(lex)

    if not tokens:
        return rest, list()

    return organize_tokens(tokens, rest)


def interpret_expression(lop, op, rop):
    if op == '=':
        if not DOTENV_VAR_NAME.match(lop):
            raise DotEnvParserError(f'Invalid variable name: {lop}')

        if not rop:
            raise DotEnvParserError(f'Nothing to assign to {lop}')

    # Other operators go here
    else:
        raise DotEnvParserError(f'Cant parse this as an expression: {lop} {op} {rop}')

    return [(lop, ''.join(rop))]


def interpret_command(cmd, args, allow_source=True, **kwargs):
    # Command parser
    if cmd == 'export':
        try:
            lop, op, *rop = args
        except ValueError:
            raise DotEnvParserError(f'Missing operands')

        return interpret_expression(lop, op, rop)

    elif cmd == 'source':
        if not allow_source:
            raise DotEnvNotAllowed("Use of 'source' is not allowed (set allow_source=True)")
        try:
            path = Path(''.join(args))
        except Exception as e:
            raise DotEnvParserError(f'Unable to parse path: {args} (reason: {e})')

        kwargs['evaluate'] = False

        return source_dotenv_path(path, **kwargs)

    # Other commands go here!
    # Add it to supported commands too
    else:
        raise DotEnvParserError(f'Unsupported command: {cmd}')


def interpret_row(tokens, **kwargs):
    # We have to deal with a simple grammar:
    # Case 1: l_operand = *r_operands  => returns [(l_operand, r_operands)]
    # Case 2: cmd *args => runs command and returns [(k1, v1), ...] or None
    # Case 2A: export l_operand = *r_operands => gets transformed into Case 1

    # Eliminates empty lists
    if not tokens:
        return None

    # Check case 2:
    if tokens[0] in DOTENV_SUPPORTED_COMMANDS:
        cmd, *args = tokens
        return interpret_command(cmd, args, **kwargs)

    else:
        # Fallback to case 1
        try:
            lop, op, *rop = tokens
        except ValueError:
            raise DotEnvParserError(f'Unknown syntax')

        return interpret_expression(lop, op, rop)


def source_dotenv_path(path, base_dir=None, **kwargs):
    try:
        path = Path(path)
    except Exception as e:
        raise DotEnvParserError(f'Unable to resolve path: {path} (reason: {e})')

    if not path.is_absolute():
        path = base_dir / path

    if path.is_dir():
        path = path / DOTENV_DEFAULT_FILE

    if not path.exists():
        raise DotEnvParserError(f'Missing file: {path}')

    # Change base_dir to path.parent
    base_dir = path.parent

    file_info = path.relative_to(base_dir)

    with path.open('r') as fp:
        return parse_dotenv(fp, base_dir=base_dir, _file_info=file_info, **kwargs)


def parse_variable_substitutions(content, defaults=None, case_sensitive=False, missing_vars=None):
    # Parse variable substitutions (${VARIABLE})
    defaults = defaults or dict()

    # It will parse based on current state (i.e. in order), than on defaults
    state = ChainMap(dict(), defaults)
    parsed_content = list()

    for k, v in content:

        if not case_sensitive:
            k = k.upper()

        for sub, var in DOTENV_VAR_SUBS.findall(v):

            if not case_sensitive:
                var = var.upper()

            var_value = state.get(var, None)

            if var_value is None:
                if missing_vars:
                    var_value = f'{{var}}'
                elif missing_vars is None:
                    var_value = ""
                else:
                    raise DotEnvParserError(f'Missing variable: {var}')

            if var_value is not None:
                v = v.replace(sub, var_value, 1)

        # Adds parsed content to state
        state[k] = v
        parsed_content += [(k, v)]

    return parsed_content


def parse_dotenv(s, allow_source=True, base_dir=None, evaluate=True, case_sensitive=False, key_format=None, prefix=None, suffix=None, parse_var_subs=True, defaults=None, missing_vars=None, _file_info=None):
    """
    Parses a string containing a typical dotenv file with some additional capabilities such as sourcing from other
    dotenv files and substituting variables.
    :param s: dotenv content to be parsed
    :param allow_source: this will include any file 'sourced' with source syntax. If True, sources will be evaluated.
    If None, they will be ignored. If False, they will raise an error.
    :param base_dir: serves as base dir to look for sourcing files, defaults to cwd.
    :param evaluate: if True, this will return a dict with all variables (similar to os.environ), otherwise returns
    a list with {var_name: value}. This parameter must be True for key filtering and variable parsing to occur.
    :param case_sensitive: sOMe_vAr != SOME_VAR, otherwise parses as if they were the same (default). Affects variable
    substitution and evaluation only.
    :param key_format: allows '{prefix}{key}{suffix}' to be parsed as 'key'. This will run at the end of the process in
    order to no mess up with variable substitution and will filter out variables that do not comply with the formatting.
    :param prefix: same as key_format="{prefix}_{key}" (notice the underscore)
    :param suffix: same as key_format='{key}_{suffix}" (notice the underscore)
    :param parse_var_subs: parse simple variable substitutions ("${VARIABLE}) based on the order they were defined.
    :param defaults: any mapping that serves as a default for variable substitution (typically os.environ)
    :param missing_vars: defaults to False. If None, missing vars will be assigned to None. If True, the parser will
    ignore them (so ${SOME_VAR} will be carried over) and if False, the parser will raise an error.

    :return: mapping with final results from dotenv parsing (similar to what you will find in os.environ)
    """
    s = s.splitlines() if isinstance(s, str) else s
    defaults = defaults or dict()
    base_dir = Path(base_dir) if base_dir else Path.cwd()
    _file_info = _file_info or '[direct]'

    if key_format:
        prefix, _, suffix = key_format.partition('{key}')
    else:
        prefix = f"{prefix}_" if prefix else ""
        suffix = f"_{suffix}" if suffix else ""

    inject_kwargs = {
        'allow_source': allow_source,
        'base_dir': base_dir,
        # Evaluate if True must happen only at the end of the chain
        'evaluate': False,
    }

    rest = list()
    output = list()

    for lineno, row in enumerate(s):
        tokens, rest = parse_row(row, rest)

        # Loops until the row is fully interpreted (i.e., rest is empty)
        while tokens or rest:
            # Gets a chunk of the row
            if tokens:
                try:
                    result = interpret_row(tokens, **inject_kwargs)
                except DotEnvException as err:
                    msg = f'{err} (@ line:{lineno} file: {_file_info})'
                    raise DotEnvParserError(msg) from err
                except Exception as err:
                    msg = f'{err} (@ line:{lineno} file: {_file_info})'
                    raise Exception(msg) from err

                if result:
                    output += result

            if rest:
                tokens, rest = organize_tokens(rest)
            else:
                break

    # Final evaluation
    if not evaluate:
        # If evaluate is set to false, the returns a list 'as is'
        return output

    # Runs final evaluation
    # Parse variable substitutions
    if parse_var_subs:
        output = parse_variable_substitutions(output, defaults=defaults, case_sensitive=case_sensitive, missing_vars=missing_vars)

    # Ignore anything that does not match formatting
    if prefix or suffix:
        output = [(k, v) for k, v in output if (not prefix or k.startswith(prefix)) and (not suffix or k.endswith(suffix))]

    # Parsing to a dict will also de-dup variables in parsing order
    return dict(**defaults, **dict(output))


def parse_dotenv_file(fp, base_dir=None, **kwargs):
    # Entrypoint for file parsing, same syntax as parse_dotenv
    base_dir = Path(base_dir) if base_dir else Path.cwd()
    return source_dotenv_path(fp, base_dir=base_dir, **kwargs)


def source_dotenv(s, safer=True, export_all=True, defaults=None):
    """
    This will run content as a bash script and returns exported environment. This will run any kind of variable
    substitution, conditionals as well as any unsafe code inside content. So BE CAREFUL!
    :param s: bash script
    :param safer: Skips direct command execution by parsing via parse_dotenv first then quoting everything.
    :param export_all: This will presume that any variable defined in the script will be exported afterwards. Only
    works if safer is True.
    :param defaults: Provide os.environ or any sort of mapping that will serve as os.environ for bash to run.
    :return: returns a dict with the resulting os.environ (please be aware of the side effects from content!)
    """
    # Based on: https://stackoverflow.com/questions/3503719/emulating-bash-source-in-python
    # Credits to https://stackoverflow.com/users/360899/lesmana

    defaults = defaults or dict()

    if safer:
        # Handles first parsing with parse_dotenv (which skips direct command execution)
        content = parse_dotenv(s, parse_var_subs=False, evaluate=False)
        if content:
            s = serialize_dotenv(content, cmd='export' if export_all else None)

    command = shlex.split(f"env -i bash -c 'source < $(echo \"{s}\")' && env")
    proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    for line in proc.stdout:
        (key, _, value) = line.partition("=")
        os.environ[key] = value
    proc.communicate()

    return dict(**defaults, **os.environ)


def serialize_dotenv_iter(content, cmd='export', line_break='\n'):
    cmd = (cmd.strip() + ' ') if cmd else ''
    line_break = line_break or '\n'
    content = content.items() if isinstance(content, Mapping) else content

    for key, value in content:
        yield f"{cmd}{key}={shlex.quote(value)}{line_break}"


def serialize_dotenv(content, cmd=None, line_break='\n'):
    return "".join(serialize_dotenv_iter(content, cmd=cmd, line_break=line_break))


def serialize_dotenv_stream(content, fp, cmd=None, line_break='\n'):
    for row in serialize_dotenv_iter(content, cmd=cmd, line_break=line_break):
        fp.write(row)


# Implements syntax equivalent to other python serializers
loads = parse_dotenv
load = parse_dotenv_file
dumps = serialize_dotenv
dump = serialize_dotenv_stream
