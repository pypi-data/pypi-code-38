import json
import re

from more_itertools.recipes import grouper

try:
    from typing import Optional, Tuple, Dict, Any
except ImportError:
    Optional = Tuple = Dict = Any = None


STRING_LITERAL_RE = (
    # Make sure the quote is not escaped
    r'(?<!\\)('
    # Triple-double
    r'"""(?:.|\n)*(?<!\\)"""|'
    # Triple-single
    r"'''(?:.|\n)*(?<!\\)'''|"
    # Double
    r'"[^\n]*(?<!\\)"(?!")|'
    # Single
    r"'[^\n]*(?<!\\)'(?!')"
    ')'
)


def _get_parenthesis_imbalance_index(text, imbalance=0):
    # type: (str, int) -> str
    """
    Return an integer where:

        - If the parenthesis are not balanced--the integer is the imbalance index at the end of the text (a negative
          number).

        - If the parenthesis are balanced--the integer is the index at which they become so (a positive integer).
    """

    index = 0
    length = len(text)

    while index < length and imbalance != 0:

        character = text[index]

        if character == '(':
            imbalance -= 1
        elif character == ')':
            imbalance += 1

        index += 1

    return index if imbalance == 0 else imbalance


class SetupScript(object):

    def __init__(self, path=None):
        # type: (Optional[str]) -> None
        self.path = path  # type: Optional[str]
        self.source = None  # type: Optional[str]
        self.setup_calls = []  # type: Sequence[SetupCall]
        self._setup_call_locations = []
        self._setup_kwargs_code = None  # type: Optional[str]
        if path is not None:
            self.open(path)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback_):
        # type: (str, str, traceback) -> None
        pass

    def open(self, path):
        # type: (str) -> None
        self.path = path
        with open(path, 'r') as setup_io:
            self.source = setup_io.read()
        self._parse()

    @property
    def _get_setup_kwargs_code(self):

        script_parts = []
        setup_call_index = 0
        character_index = 0
        parenthesis_imbalance = 0
        in_setup_call = False
        self._setup_call_locations = []

        for code, string_literal in grouper(re.split(STRING_LITERAL_RE, self.source), 2, None):

            if code:

                for preceding_code, setup_call in grouper(re.split(r'(\bsetup[\s]*\()', code), 2, None):

                    script_parts.append(preceding_code)

                    # Determine where the setup call ends, if we are inside it
                    if in_setup_call:

                        # We don't care about parenthesis in comments
                        relevant_preceding_code = preceding_code
                        if '#' in relevant_preceding_code:
                            relevant_preceding_code = relevant_preceding_code.split('#')[0]

                        # Determine if/where the parenthetical ends, or the imbalance resulting
                        parenthesis_imbalance = _get_parenthesis_imbalance_index(
                            relevant_preceding_code,
                            parenthesis_imbalance
                        )

                        # If `imbalance` is positive--it's the index where the imbalance ends
                        if parenthesis_imbalance > 0:
                            self._setup_call_locations[-1][-1] = character_index + parenthesis_imbalance
                            parenthesis_imbalance = 0
                            in_setup_call = False

                    # Parse the setup call
                    if setup_call:
                        self._setup_call_locations.append([character_index + len(preceding_code), None])
                        parenthesis_imbalance = -1
                        in_setup_call = True
                        script_parts.append('SETUP_KWARGS[%s] = dict(' % str(setup_call_index))
                        setup_call_index += 1

                character_index += len(code)

            if string_literal:

                script_parts.append(string_literal)
                character_index += len(string_literal)

        script_parts.insert(
            0,
            'SETUP_KWARGS = [%s]\n' % ', '.join(['None'] * setup_call_index)
        )

        return ''.join(script_parts)

    def _get_setup_kwargs(self):
        # type: (...) -> Sequence[dict]
        """
        Return an array of dictionaries where each represents the keyword arguments to a `setup` call
        """
        name_space = {}

        try:
            exec(self._get_setup_kwargs_code, name_space)
        except:
            # Only raise an error if the script could not finish populating all of the setup keyword arguments
            if not (
                'SETUP_KWARGS' in name_space and
                name_space['SETUP_KWARGS'] and
                name_space['SETUP_KWARGS'][-1] is not None
            ):
                raise

        return name_space['SETUP_KWARGS']

    def _parse(self):
        # type: (Sequence[dict]) -> None
        """
        Set the arguments for the setup calls
        """

        parts = []
        setup_kwargs = self._get_setup_kwargs()
        length = len(setup_kwargs)
        character_index = 0

        for index in range(length):
            parts.append(
                self.source[
                    character_index:
                    self._setup_call_locations[index][0]
                ]
            )
            source = self.source[
                self._setup_call_locations[index][0]:
                self._setup_call_locations[index][1]
            ]
            self.setup_calls.append(
                SetupCall(
                    self,
                    source=source,
                    keyword_arguments=setup_kwargs[index]
                )
            )

    def __str__(self):
        # type: (...) -> str
        parts = []
        length = len(self.setup_calls)
        character_index = 0

        for index in range(length):
            parts.append(
                self.source[
                    character_index:
                    self._setup_call_locations[index][0]
                ]
            )
            setup_call = self.setup_calls[index]
            parts.append(str(setup_call))
            if index < length - 1:
                character_index = self._setup_call_locations[index + 1][0]
            index += 1

        character_index = self._setup_call_locations[-1][1] + 1
        parts.append(self.source[character_index:])

        return ''.join(parts)

    def save(self, path=None):
        # type: (Optional[str]) -> bool

        if path is None:
            path = self.path

        modified = False
        existing_source = None
        new_source = str(self)

        try:
            with open(path, 'r') as setup_io:
                existing_source = setup_io.read()
        except FileNotFoundError:
            pass

        if new_source != existing_source:
            modified = True
            with open(path, 'w') as setup_io:
                setup_io.write(new_source)

        return modified


class SetupCall(object):

    def __init__(
        self,
        setup_script,
        source,
        keyword_arguments
    ):
        # type: (SetupScript, int, int, str, dict) -> None

        self.setup_script = setup_script
        self.source = source  # type: str

        self._keyword_arguments = keyword_arguments  # type: dict

        indentation = ''
        parameter_indentation = ''
        expand_tabs = True
        lines = self.source.split('\n')

        if len(lines) > 1:
            line = lines[-1]
            match = re.match(r'^[ ]+', line)
            if match:
                group = match.group()
                if group:
                    indentation = group
            if not indentation:
                match = re.match(r'^[\t]+', line)
                if match:
                    group = match.group()
                    if group:
                        indentation = group
                        expand_tabs = False
            parameter_indentation = indentation

        if len(lines) > 2:
            line = self.source.split('\n')[1]
            match = re.match(r'^[ ]+', line)
            if match:
                group = match.group()
                if group:
                    parameter_indentation = group
            if not parameter_indentation:
                match = re.match(r'^[\t]+', line)
                group = match.group()
                if group:
                    parameter_indentation = group
                    expand_tabs = False

        self._indentation = indentation
        self._parameter_indentation = parameter_indentation
        self._expand_tabs = expand_tabs

    def __str__(self):
        return self.source

    def repr(self):
        # type: (...) -> str
        return '\n'.join([
            'setuptools_setup_versions.parse.SetupCall(\n',
            '   %s,\n' % repr(self.source),
            '   %s,\n' % repr(self._keyword_arguments),
            ')'
        ])

    def __setitem__(self, key, value):
        # type: (str, Any) -> None

        if self[key] != value:

            source_parts = re.split(
                r'(\b%s[\s]*=)' % key,
                self.source
            )  # type: Sequence[str]
            existing_key_value_source = None

            if len(source_parts) > 2:

                source_parts[-1] = source_parts[-1].rstrip(')')
                self.name_space = {}

                for i in range(2, len(source_parts), 2):

                    source_value_representation_parts = []
                    potential_source_value_representation_parts = source_parts[i].split(',')

                    for source_value_representation_part in potential_source_value_representation_parts:
                        source_value_representation_parts.append(source_value_representation_part)
                        try:
                            exec(
                                'value = ' + ','.join(source_value_representation_parts),
                                self.name_space
                            )
                            break
                        except SyntaxError:
                            pass

                    existing_key_value_source = (
                        ''.join(source_parts[-2]) + ','.join(source_value_representation_parts)
                    ).rstrip()

                    break

            indent = len(self._parameter_indentation) - len(self._indentation)
            key_value_source = key + '=' + json.dumps(value, indent=indent)

            if self._parameter_indentation:
                key_value_source_lines = key_value_source.split('\n')
                if len(key_value_source_lines) > 1:
                    for i in range(1, len(key_value_source_lines)):
                        key_value_source_lines[i] = self._parameter_indentation + key_value_source_lines[i]
                key_value_source = '\n'.join(key_value_source_lines)

            if existing_key_value_source is None:

                lines = self.source.split('\n')
                if len(lines) > 1:
                    self.source = (
                        '\n'.join(lines[:-1]).rstrip(' ,') + ',\n' +
                        self._parameter_indentation + key_value_source +
                        lines[-1]
                    )
                else:
                    self.source = self.source.rstrip(',) ') + ', ' + key_value_source + ')'

            else:

                self.source = self.source.replace(existing_key_value_source, key_value_source)

            self._keyword_arguments[key] = value

    def __getitem__(self, key):
        # type: (str) -> Any
        return self._keyword_arguments[key]

    def items(self):
        return self._keyword_arguments.items()

    def __contains__(self, item):
        # type: (str) -> bool
        return item in self._keyword_arguments
