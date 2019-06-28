'''
Preprocessor for Foliant documentation authoring tool.
Removes section meta-data from the document and adds seeds.
'''
from yaml import load, Loader

from foliant.preprocessors.base import BasePreprocessor
from foliant.meta_commands.generate import YFM_PATTERN, SECTION_PATTERN


class Preprocessor(BasePreprocessor):
    defaults = {
        'seeds': {}  # contains a format-string with optional {value} placeholder
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = self.logger.getChild('meta')

        self.logger.debug(f'Preprocessor inited: {self.__dict__}')

    def add_seeds(self, content: str, pattern, leave_meta=False) -> str:
        '''
        Add seeds to content: format-strings with {value} replaced by seed
        value from section meta.
        if leave_meta is False, the yaml definition of meta will be removed.
        '''
        def sub(match):
            result = match.group(0) if leave_meta else ''
            seeds = self.options['seeds']
            yfm = load(match.group('yaml'), Loader) or {}
            if seeds:
                for key, val in yfm.items():
                    if key in seeds:
                        result += '\n\n' + seeds[key].replace('{value}', val)
            return result
        return pattern.sub(sub, content)

    def process_meta_blocks(self, content: str) -> str:
        '''
        Process all meta blocks:
        remove those which represent sections, leave YFMs, and add seeds
        '''
        result = self.add_seeds(content, YFM_PATTERN, leave_meta=True)
        result = self.add_seeds(content, SECTION_PATTERN, leave_meta=False)
        return result

    def apply(self):
        self.logger.info('Applying preprocessor')

        for markdown_file_path in self.working_dir.rglob('*.md'):
            self.logger.debug(f'Processing Markdown file: {markdown_file_path}')

            with open(markdown_file_path, encoding='utf8') as markdown_file:
                content = markdown_file.read()

            with open(markdown_file_path, 'w', encoding='utf8') as markdown_file:
                markdown_file.write(self.process_meta_blocks(content))

        self.logger.info('Preprocessor applied')
