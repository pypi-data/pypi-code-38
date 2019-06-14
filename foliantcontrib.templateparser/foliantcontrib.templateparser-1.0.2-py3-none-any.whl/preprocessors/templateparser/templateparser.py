'''
Template parser preprocessor for Foliant.
'''

import pkgutil
import yaml

import foliant.preprocessors.templateparser.engines

from . import engines
from importlib import import_module

from foliant.preprocessors.utils.combined_options import (Options,
                                                          CombinedOptions,
                                                          validate_in,
                                                          yaml_to_dict_convertor,
                                                          path_convertor)
from foliant.preprocessors.utils.preprocessor_ext import (BasePreprocessorExt,
                                                          allow_fail)


OptionValue = int or float or bool or str


def get_engines():
    '''
    Get dictionary with available template engines.
    Key - engine name, value - engine class
    '''
    result = {}
    for importer, modname, ispkg in pkgutil.iter_modules(engines.__path__):
        module = import_module(f'foliant.preprocessors.templateparser.engines.{modname}')
        if hasattr(module, 'TemplateEngine'):
            result[modname] = module.TemplateEngine
    return result


class Preprocessor(BasePreprocessorExt):
    defaults = {
        'engine_params': {}
    }
    engines = get_engines()
    tags = ('template', *engines.keys())
    tag_params = ('engine',
                  'context',
                  'ext_context',
                  'engine_params')  # all other params will be redirected to template

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.logger.getChild('templateparser')

        self.logger.debug(f'Preprocessor inited: {self.__dict__}')

    @allow_fail('Failed to render template.')
    def process_template_tag(self, block) -> str:
        """
        Function for processing tag. Send the contents to the corresponging
        template engine along with parameters from tag and config, and
        <content_file> path. Replace the tag with output from the engine.
        """
        tag_options = Options(self.get_options(block.group('options')),
                              validators={'engine': validate_in(self.engines.keys())},
                              convertors={'context': yaml_to_dict_convertor,
                                          'engine_params': yaml_to_dict_convertor,
                                          'ext_context': path_convertor})
        options = CombinedOptions({'config': self.options,
                                   'tag': tag_options},
                                  priority='tag')

        tag = block.group('tag')
        if tag == 'template':  # if "template" tag is used — engine must be specified
            if 'engine' not in options:
                self._warning('Engine must be specified in the <template> tag. Skipping.',
                              self.get_tag_context(block))
                return block.group(0)
            engine = self.engines[options['engine']]
        else:
            engine = self.engines[tag]

        context = {}
        # external context is loaded first, it has lowest priority
        if 'ext_context' in options:
            try:
                context = dict(yaml.load(open((self.current_filepath).parent /
                                              options['ext_context'], encoding="utf8"),
                                         yaml.Loader))
            except FileNotFoundError as e:
                self._warning(f'External context file {options["ext_context"]} not found',
                              error=e)
        # all unrecognized params are redirected to template engine params
        context.update({p: options[p] for p in options if p not in self.tag_params})
        # add options from "context" param
        context.update(options.get('context', {}))
        template = engine(block.group('body'),
                          context,
                          options.get('engine_params', {}),
                          self.current_filepath)
        return template.build()

    def apply(self):
        self._process_tags_for_all_files(self.process_template_tag)

        self.logger.info('Preprocessor applied')
