r"""Pre-defined command line parsers supported by Friendly Shell APIs

All Friendly Shell command lines are expected to begin with a command name,
followed by 0 or more input parameters as shown below:

    <command_token>[<parameter_tokens>]

The command portion of each line must map command names to Python class methods
that are prefixed with the characters "do\_" (ie: "do\_exit()"). Because of this
commands must meet the same naming restrictions as Python class methods. Thus
most Friendly Shells line parsers will want to leverage the :class:`meth`
default_command_parser function to parse the first token of their command lines.
Also, for convenience all command token parsers are expected to return a named
token with the label 'command' associated with it.

The optional list of parameter tokens may satisfy whatever restrictions are
desired by a particular command. Since they need not be mapped to Python class
methods they do not need to be bound by the same naming rules as the command
token. Finally, the list of input parameters - when provided - are expected to
return a named token with the label 'params', which will define a list of 1 or
more input parameters to be provided to the command.

Below you will find some helper functions that provide pre-built grammars for
some common command and parameter token styles so users of the library need not
always write their own.
"""
import pyparsing as pp


def default_line_parser():
    """Gets the default command line parser used by the Friendly Shell APIs

    :rtype: :class:`pyparsing.Parser`"""
    return default_command_token() + \
           (pp.lineEnd ^ quoted_space_sep_params_token())


def default_command_token():
    """token parser that satisfies the requirements of the FShell interpreter

    Meets the default naming requirements of the Friendly Shell interpreter,
    ensuring that command names may be safely mapped to Python class methods.
    The resulting token will be labelled 'command' as required by the
    Friendly Shell APIs.

    :rtype: :class:`pyparsing.Parser`
    """

    return pp.Word(pp.printables).setResultsName('command')


def quoted_space_sep_params_token():
    r"""Gets a token parser that supports

    This parser expects all commands to take the following form:
        <command_name>[ <optional_param1> <optional_param2>...]<eol>

    The <command_name> maps to a method of this class or a descendent of it with
    the same name but with a prefix of "do\_". As a result tokens for commands
    must adhere to the same restrictions as a typical Python class method.

    Commands may optionally accept parameters if desired. Parameters are
    provided on the same line as the command and are separated by spaces. Each
    parameter may use any printable character since they are translated to
    Python strings during translation and thus need not be restricted to the
    same criteria as commands. Also, if a parameter needs to contain embedded
    spaces then it must be wrapped in quotation marks. Single or double quotes
    will work. Further, if you need to embed quotation marks within your string
    simply wrap the inner quotes with outer quotes of the opposite style.

    The command token can be accessed by named attribute 'command', and the list
    of any parameters provided on the line can be acessed by the named attribute
    'params'.

    TODO: Add support for escaping quote characters when embedded in strings
    delimited with the same quote style, as in "\"hello\" world"

    :rtype: :class:`pyparsing.Parser`"""

    # token for a command parameter with no spaces embedded in it
    simple_parameter = pp.Word(pp.printables, excludeChars='"\'')

    # Complex parameter with embedded spaces delimited by single quote
    # characters. Such params may also contain embedded double quotes
    single_quoted_parameter = pp.Combine(
        pp.Word("'") +
        pp.Optional(pp.Word(pp.printables + ' ', excludeChars="'")) +
        pp.Optional(pp.Word("'"))
    )

    # Complex parameter with embedded spaces delimited by double quote
    # characters. Such params may also contain embedded single quotes
    double_quoted_parameter = pp.Combine(
        pp.Word('"') +
        pp.Optional(pp.Word(pp.printables + ' ', excludeChars='"')) +
        pp.Optional(pp.Word('"'))
    )

    # Token represent an arbitrary parameter which may be one of the quoted or
    # simple formatter params defined above. NOTE: pyparsing uses ^ as a
    # shorthand for OR operator
    parameter = \
        simple_parameter ^ single_quoted_parameter ^ double_quoted_parameter

    # A command line may have multiple parameters separated by spaces. Below
    # is the token encapsulating all params in a command line. These will be
    # parsed into a list of tokens accessible by the 'params' named parameter
    params = pp.OneOrMore(parameter).setResultsName('params')

    return params


if __name__ == "__main__":
    pass
