'''
Arbitrary anchors for Foliant.
'''

import os
import re

from urllib.parse import urlparse, urlencode, parse_qsl, urlunparse

from foliant.preprocessors.utils.combined_options import (CombinedOptions,
                                                          boolean_convertor)
from foliant.preprocessors.utils.preprocessor_ext import (BasePreprocessorExt,
                                                          allow_fail)

OptionValue = int or float or bool or str


AS_IMG = '![]({link})'
AS_OBJECT = '<object data="{link}" type="image/svg+xml"></object>'


def get_ext_from_url(url: str):
    """get an image extension from a link to it"""
    return os.path.splitext(urlparse(url).path)[1]


def is_svg(url: str):
    """determine if image format is svg"""
    return get_ext_from_url(url) == '.svg'


def apply_vars(vars_: dict, value: str):
    """replace variables in value by their values from dict"""
    result = value
    for var, repl in vars_.items():
        p = re.compile(f'\\$\\{{{var}\\}}', re.IGNORECASE)
        result = p.sub(repl, result)
    return result

def gen_link(badge_url):
    """Try to generate a link which should be added to the badge"""
    patterns =  {
        r'\g<protocol>://\g<host>/browse/\g<issue>': (r'/jira/issue/(?P<protocol>.+?)/(?P<host>.+)/(?P<issue>.+)\.\w+',),
        r'https://pypi.org/project/\g<project>': (r'/pypi/\w+/(?P<project>.+)\.\w+',)
    }
    for repl, exprs in patterns.items():
        for expr in exprs:
            res = re.search(expr, badge_url)
            if res:
                return re.sub(expr, repl, res.group(0))

def add_params_to_url(url: str, params: dict):
    """add query params to url from params dict (with replace)"""
    url_parts = list(urlparse(url))
    query = dict(parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urlencode(query)
    return urlunparse(url_parts)

class Preprocessor(BasePreprocessorExt):
    defaults = {
        'targets': [],
        'server': 'https://img.shields.io',
        'as_object': True,
        'add_link': True,
        'vars': {},
    }
    tags = ('badge',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = self.logger.getChild('badges')

        self.logger.debug(f'Preprocessor inited: {self.__dict__}')

    @allow_fail()
    def process_badges(self, block) -> str:
        """Replace <badge> tags with an image or an svg-object tag"""
        if self.options['targets'] and\
                self.context['target'] not in self.options['targets']:
            self.logger.debug(f'{self.context["target"]} not in targets, removing all badge tags')
            return ''  # remove tags for other targets

        options = CombinedOptions({'main': self.options,
                                   'tag': self.get_options(block.group('options'))},
                                  convertors={'as_object': boolean_convertor,
                                              'add_link': boolean_convertor,
                                              'server': lambda x: x.rstrip('/')},
                                  priority='tag')
        value = block.group('body').lstrip('/')
        value = apply_vars(options['vars'], value)
        if not value:
            self._warning('Path to badge not specified. Skipping',
                          context=self.get_tag_context(block))
            return block.group(0)

        if value.startswith('http'):
            link = value
        else:
            link = '/'.join((options['server'], value))

        if options['add_link']:
            badge_link = gen_link(link)
            if badge_link:
                link = add_params_to_url(link, {'link': badge_link})

        if self.context['target'] not in ('pdf', 'docx') and\
                is_svg(link) and options['as_object']:
            return AS_OBJECT.format(link=link)
        else:
            return AS_IMG.format(link=link)

    def apply(self):
        self._process_tags_for_all_files(self.process_badges)
        self.logger.info('Preprocessor applied')
