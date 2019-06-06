import os
import re
import regex
from pystache import Renderer

# TODO: implement the proper RegEx for the convert methods. Only work from '-' right now
yes_no = ['y', 'n']


def convert_to_snake(string):
    return re.sub(r'[-./|\s]', '_', cap_sanitized(string)).lower()


def convert_to_dashes(string):
    return re.sub(r'[._/|\s]', '-', cap_sanitized(string)).lower()


def convert_to_periods(string):
    return re.sub(r'[-_/|\s]', '.', cap_sanitized(string)).lower()


def convert_to_slashes(string):
    return re.sub(r'[-_.|\s]', '/', cap_sanitized(string)).lower()


def convert_to_lower_with_spaces(string):
    return convert_to_caps_with_spaces(string).lower()


def convert_to_camel(string):
    all_caps = convert_to_caps_no_spaces(string)
    return all_caps[0].lower() + all_caps[1:]


def convert_to_caps_with_spaces(string):
    capitalized_words = extract_words(string)
    return str.join(' ', capitalized_words)


def convert_to_caps_no_spaces(string):
    capitalized_words = extract_words(string)
    return str.join('', capitalized_words)


def extract_words(string):
    string = convert_to_dashes(string)
    words = string.split('-')
    capitalized_words = []
    for word in words:
        capitalized_words.append(word.capitalize())
    return capitalized_words


def cap_sanitized(string: str):
    index = 0
    for letter in string:
        if letter.isupper():
            if index > 0:
                string = string[:index] + '|' + letter.lower()
        index += 1
    return string


def render_template_to_directory(destination: str, template: str, parameters: dict):
    overwrite_file(destination, renderer.render(open(template, 'r').read(), parameters))


def render_destination_path(destination: str, parameters: dict) -> str:
    return renderer.render(destination, parameters)


def overwrite_file(file, content):
    directory_name = os.path.dirname(file)
    if directory_name != '':
        os.makedirs(directory_name, exist_ok=True)
    f = open(file, 'w')
    f.write(content)
    f.close()


def handle_prompt(prompt: dict):
    prompt_type = prompt.get('type')
    if not prompt_type:
        prompt_type = 'STRING'
    if prompt_type == 'BOOL':
        prompt['options'] = yes_no
    return prompt_user(prompt)


def prompt_user(prompt: dict):
    text = prompt['text']
    default = prompt.get('default')
    options = prompt.get('options')
    validations = prompt.get('validations')
    text = format_prompt_text(text, default, options)
    input_response = input(text)
    if input_response == "":
        if default is not None:
            input_response = default
    valid = is_valid_input(input_response, validations)
    while not valid:
        text = f'{text[0:-2]} ({get_validation_strings(validations)}): '
        input_response = input(text)
        valid = is_valid_input(input_response, validations)
    return input_response


def format_prompt_text(text, default, options):
    if default is not None and not "":
        text += f" ({default})"
    if options is not None and len(options) > 0:
        text += f" [{options}]"
    text += ": "
    return text


def get_validation_strings(validations: list) -> str:
    validation_string = "The following validations must be met to continue: "
    for validation in validations:
        evaluation = validation['evaluation']
        value = validation['value']
        if evaluation:
            if equals_ignore_case(evaluation, 'REGEX'):
                text = f'Must match regular expression: {value}. '
            elif equals_ignore_case(evaluation, 'GREATER_THAN'):
                text = f'Must be greater than: {value}. '
            elif equals_ignore_case(evaluation, 'LESS_THAN'):
                text = f'Must be less than: {value}. '
            else:
                raise AttributeError(f'Invalid evaluation type for validations: {evaluation}')
            validation_string += text
    return validation_string[:-1]


def yes_no_to_bool(response: str):
    if len(response) > 0:
        return equals_ignore_case(response[0], 'y')
    return False


def is_valid_input(input_response: str, validations: list) -> bool:
    """
    Will compare for valid input against a user response.

    At the moment, using the greater than or less than comparator is only support for integer types.

    :param input_response:
    :param validations:
    :return:
    """
    valid = True
    if validations:
        for validation in validations:
            evaluation = validation['evaluation']
            value = validation['value']
            if evaluation:
                if equals_ignore_case(evaluation, 'REGEX'):
                    valid = regex.match(value, input_response)
                elif equals_ignore_case(evaluation, 'GREATER_THAN'):
                    valid = int(input_response) > value
                elif equals_ignore_case(evaluation, 'LESS_THAN'):
                    valid = int(input_response) < value
                elif equals_ignore_case(evaluation, 'BOOL'):
                    valid = yes_no_to_bool(input_response) == value
                else:
                    raise AttributeError(f'Invalid evaluation type for validations: {evaluation}')
                if not valid:
                    return valid
    return valid


def equals_ignore_case(candidate: str, target: str):
    return candidate.lower() == target.lower()


renderer = Renderer()
