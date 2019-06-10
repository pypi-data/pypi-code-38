'''Preprocessor for admonitions'''

import re

from foliant.preprocessors.utils.preprocessor_ext import (BasePreprocessorExt,
                                                          allow_fail)


def pandoc(type_: str,
           title: str,
           lines: list):
    template = "{body}\n\n"
    header = title if title is not None else type_
    if header:
        template = '> **{header}**\n>\n' + template
    body = '\n'.join(['> ' + l for l in lines])
    return template.format(header=header, body=body)


def slate(type_: str,
          title: str,
          lines: list):
    type_to_class = {'error': 'warning',
                     'danger': 'warning',
                     'caution': 'warning',
                     'info': 'notice',
                     'note': 'notice',
                     'tip': 'notice',
                     'hint': 'notice', }
    template = '<aside class="{class_}">{body}</aside>\n\n'
    class_ = type_to_class.get(type_, type_)
    body = '\n'.join(lines)
    return template.format(class_=class_, body=body)


class Preprocessor(BasePreprocessorExt):
    backend_processors = {
        'pandoc': pandoc,
        'slate': slate,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = self.logger.getChild('admonitions')

        self.logger.debug(f'Preprocessor inited: {self.__dict__}')
        self.pattern = re.compile(r'!!! (?P<type>\w+)(?: +"(?P<title>.*)")?\n(?P<content>(?:(?:    |\t).*\n|\n)+)')

    @allow_fail('Failed to process admonition. Skipping.')
    def _process_admonition(self, block):
        type_ = block.group('type').lower()
        title = block.group('title')
        lines = []

        for l in block.group('content').split('\n'):
            if not l:
                # break
                lines.append('')
            if l.startswith('    '):
                lines.append(l[4:])
            else:  # starts with tab
                lines.append(l[1:])

        while lines[-1] == '':  # remove empty lines at the end
            lines.pop()

        processor = self.backend_processors[self.context['backend']]
        return processor(type_, title, lines)

        self.context['target']

    def apply(self):
        if self.context['backend'] in self.backend_processors:
            self._process_tags_for_all_files(self._process_admonition)

        self.logger.info(f'Preprocessor applied')
