import yaml
import re
import traceback

from typing import Dict
from pathlib import Path
from foliant.preprocessors.base import BasePreprocessor
from foliant.utils import output

OptionValue = int or float or bool or str


def allow_fail(msg='Failed to process tag. Skipping.'):
    """
    decorator for tag processing function
    If function failes for some reason, warning is issued but preprocessor
    doesn't terminate. In this case the tag remains unchanged.
    """
    def decorator(func):
        def wrapper(self, match):
            try:
                return func(self, match)
            except Exception as e:
                self._warning(f'{msg} {e}',
                              context=self.get_tag_context(match),
                              error=e)
                return match.group(0)
        return wrapper
    return decorator


class BasePreprocessorExt(BasePreprocessor):
    """Extension of BasePreprocessor with useful helper methods"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_filename = ''

    @staticmethod
    def get_options(options_string: str) -> Dict[str, OptionValue]:
        '''
        *** BasePreprocessor static method overriden ***
        Get a dictionary of typed options from a string with XML attributes.

        :param options_string: String of XML attributes

        :returns: Dictionary with options
        '''

        if not options_string:
            return {}

        option_pattern = re.compile(
            r'(?P<key>[A-Za-z_:][0-9A-Za-z_:\-\.]*)=(\'|")(?P<value>.+?)\2',
            flags=re.DOTALL
        )

        return {
            option.group('key'): yaml.load(option.group('value'), yaml.Loader)
            for option in option_pattern.finditer(options_string)
        }

    @staticmethod
    def get_tag_context(match, limit=100, full_tag=False):
        '''
        Get context of the tag match object.

        Returns a string with <limit> symbols before match, the match string and
        <limit> symbols after match.

        If full_tag == False, matched string is limited too: first <limit>/2
        symbols of match and last <limit>/2 symbols of match.
        '''

        source = match.string
        start = max(0, match.start() - limit)  # index of context start
        end = min(len(source), match.end() + limit)  # index of context end
        span = match.span()  # indeces of match (start, end)
        result = '...' if start != 0 else ''  # add ... at beginning if cropped
        if span[1] - span[0] > limit and not full_tag:  # if tag contents longer than limit
            bp1 = match.start() + limit // 2
            bp2 = match.end() - limit // 2
            result += f'{source[start:bp1]} <...> {source[bp2:end]}'
        else:
            result += source[start:end]
        if end != len(source):  # add ... at the end if cropped
            result += '...'
        return result

    def _warning(self,
                 msg: str,
                 context='',
                 error: Exception = None):
        '''
        Log warning and print to user.

        If debug mode — print also context (if sepcified) and error (if specified).

        msg — message which should be logged;
        context (optional) — tag context got with get_tag_context function. If
                             specified — will be logged. If debug = True it
                             will also go to STDOUT.
        '''
        output_message = ''
        if self.current_filename:
            output_message += f'[{self.current_filename}] '
        output_message += msg + '\n'
        if context:
            log_message = output_message + f'Context:\n---\n{context}\n---\n'
        if error:
            tb_str = traceback.format_exception(etype=type(error),
                                                value=error,
                                                tb=error.__traceback__)
            log_message = log_message + '\n'.join(tb_str)
        if self.debug:
            output_message = log_message
        output(f'WARNING: {output_message}', self.quiet)
        self.logger.warning(log_message)

    def _process_tags_for_all_files(self,
                                    func,
                                    log_msg: str = 'Applying preprocessor'):
        '''Apply function func to all Markdown-files in the working dir'''
        self.logger.info(log_msg)
        for markdown_file_path in self.working_dir.rglob('*.md'):
            self.current_filepath = Path(markdown_file_path)
            self.current_filename = str(self.current_filepath.
                                        relative_to(self.working_dir))

            with open(markdown_file_path,
                      encoding='utf8') as markdown_file:
                content = markdown_file.read()

            processed_content = self.pattern.sub(func, content)

            if processed_content:
                with open(markdown_file_path,
                          'w',
                          encoding='utf8') as markdown_file:
                    markdown_file.write(processed_content)
        self.current_filename = ''
