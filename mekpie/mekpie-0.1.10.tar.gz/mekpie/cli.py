from functools                   import wraps
from re                          import sub, DOTALL
from sys                         import stderr
from prompt_toolkit              import print_formatted_text, HTML, prompt
from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion

import mekpie.debug as debug

config_layer = 0

class SuggestFromOptions(AutoSuggest):

    def __init__(self, options):
        self.options = options

    def get_suggestion(self, buffer, document):
        text = document.text.rsplit('\n', 1)[-1]
        if text.strip():
            for option in self.options:
                if option.startswith(text):
                    return Suggestion(option[len(text):])

def cli_config(name):
    def cli_config_decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            global config_layer
            tell(f'┌ Configuring {name}...')
            config_layer += 1
            result = fn(*args, **kwargs)
            config_layer -= 1
            tell(f'└ {name} configured!')
            return result
        return wrapper
    return cli_config_decorator

def fix_text(text):
    # escape < and >
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    # replace keywordss
    text = sub(r'`(.*?)`', r'<ansimagenta>\g<1></ansimagenta>', text)
    # replace errors
    text = sub(r'!! (.*)', r'<ansired>\g<1></ansired>', text)
    # replace logs
    text = sub(r'\[LOG\] (.*)', r'<ansiblue>[LOG] \g<1></ansiblue>', text, flags=DOTALL)
    return text

def tell(message, out=True, **kwargs):
    header  = '│ ' * config_layer
    message = message.strip().replace('\n', f'\n{header}')
    result  = HTML(fix_text(f'{header}{message} '))
    if (out):
        print_formatted_text(result, **kwargs)
    return result

def yell(message, out=True, **kwargs):
    header  = '│ ' * config_layer
    message = message.strip().replace('\n', f'\n{header}')
    result  = HTML(fix_text(f'{header}<ansired>{message}</ansired>'))
    if (out):
        print_formatted_text(result, **kwargs)
    return result

def panic(message=None, **kwargs):
    if message is None:
        exit(1)
    tell(f'{message}', file=stderr, end='\n\n', **kwargs)

    if debug.debug:
        raise Exception('Debug Exception')
    else:
        exit(1)

def log(value):
    if debug.debug:
        tell(f'[LOG] {str(value).strip()}')
    return value

def ask(question, default=None, options=None, validator=None):
    message, error = question
    suggestor = SuggestFromOptions(options) if options else None
    while True:
        footer = ':' if not default else f' (default `{default}`):'
        value = prompt(tell(f'{message}{footer}', False), auto_suggest=suggestor)
        if value == '' and default:
            value = default
        if ((options and value in options)
            or (validator and validator(value))
            or (not validator and not options)
        ):
            tell(f'Selected `{value}`.')
            return value
        yell(error.format(value))