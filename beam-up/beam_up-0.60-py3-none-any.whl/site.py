from .settings import SETTINGS
from .config import update
from urllib.parse import urlparse
from collections import defaultdict
import importlib
import logging
import copy
import os

from beam.config import load_config

logger = logging.getLogger(__name__)


class Site(object):

    """
    Describes a site.
    """

    def __init__(self, config):
        self.config = copy.deepcopy(config)
        self._original_config = config
        self.settings = {
            'processors' : SETTINGS['processors'].copy(),
            'loaders' : SETTINGS['loaders'].copy(),
            'builders' : SETTINGS['builders'].copy(),
        }
        self._theme_config = None
        self._translations = None
        self.process_config()

    @property
    def title(self):
        return self.config.get('title', '')

    @property
    def subtitle(self):
        return self.config.get('subtitle', '')

    @property
    def src_path(self):
        return self.config.get('src-path', 'src')

    @property
    def build_path(self):
        return self.config.get('build-path', 'build')

    @property
    def path(self):
        return self.config.get('path','/')

    @property
    def translations(self):
        if self._translations is not None:
            return self._translations
        translations = {}
        for d in (self.theme_config, self.config):
            if 'translations' in d:
                for key, trs in d['translations'].items():
                    if not key in translations:
                        translations[key] = {}
                    translations[key].update(trs)
        self._translations = translations
        return translations

    @property
    def theme_config(self):
        if self._theme_config is not None:
            return self._theme_config
        config_path = os.path.join(self.theme_path, 'theme.yml')
        if os.path.exists(config_path):
            self._theme_config = load_config(config_path)
        else:
            self._theme_config = {}
        return self._theme_config

    @property
    def theme_path(self):
        return self.config.get('theme-path', 'theme')

    def process_config(self):
        if '$all' in self.config.get('languages', {}):
            all_params = self.config['languages']['$all']
            del self.config['languages']['$all']
            for language, params in self.config['languages'].items():
                update(params, all_params)
        if 'builders' in self.config:
            self.settings['builders'].extend(self.config['builders'])

    def translate(self, language, key, *args, **kwargs):
        translations = self.translations
        if not isinstance(key, (list, tuple)):
            kc = key.split('.')
        else:
            kc = key
        cv = translations
        for elem in kc:
            if not elem in cv:
                return "[no translation for key {}]".format(key)
            cv = cv[elem]
        if not language in cv or not cv[language]:
            return "[no translation for language {} and key {}]".format(language, key)
        return cv[language].format(*args, **kwargs)

    def get_language_prefix(self, language):
        return self.config['languages'][language].get('prefix', language)

    def get_language_link_prefix(self, language):
        return self.config['languages'][language].get('link-prefix', self.get_language_prefix(language))

    def get_src_path(self, path):
        return os.path.abspath(os.path.join(self.src_path, path))

    def get_build_path(self, path):
        return os.path.abspath(os.path.join(self.build_path, path))

    def get_link_dst(self, slug, language, prefix='', extension='html'):
        suffix = ''
        if extension:
            suffix = '.{}'.format(extension)
        return os.path.join(self.get_language_link_prefix(language), prefix, slug)+suffix

    def get_dst(self, slug, language, prefix='', extension='html'):
        suffix = ''
        if extension:
            suffix = '.{}'.format(extension)
        return os.path.join(self.get_language_prefix(language), prefix, slug)+suffix

    def parse_objs(self, objs, language, prefix=''):
        parsed_objs = []
        for obj in objs:
            obj = obj.copy()
            parsed_objs.append(obj)
            if not 'src' in obj:
                #this is just a category page without a source
                continue
            extension = obj.get('extension', 'html')
            if not 'slug' in obj:
                obj['slug'] = ''.join(os.path.basename(obj['src']).split('.')[:-1])
            if not 'dst' in obj:
                obj['dst'] = self.get_dst(obj['slug'], language, prefix, extension=extension)
            if not 'link' in obj:
                obj['link'] = self.get_link_dst(obj['slug'], language, prefix, extension=extension)
            if obj['src'].find('://') == -1:
                obj['src'] = 'file://{}'.format(obj['src'])
            #if not type is given, we use the extension to determine it
            if not 'type' in obj:
                s = obj['src'].split('.')
                if len(s) < 2:
                    raise ValueError
                obj['type'] = s[-1]
        return parsed_objs

    def write(self, content, path):
        logger.info("Writing content to {}".format(path))
        full_path = self.get_build_path(path)
        dirname = os.path.dirname(full_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(full_path, 'w') as output_file:
            output_file.write(content)

    def url(self, language):
        return self.config['languages'][language].get('url', self.config.get('url', ''))

    def full_href(self, language, url):
        href = self.href(language, url)
        return '{}{}'.format(self.url(language), href)

    def href(self, language, url):
        link = self.get_link(language, url)
        if link:
            hide_extensions = self.config.get('hide-href-extensions', [])
            for extension in hide_extensions:
                # we do not remove the entire link as that breaks it
                if link.endswith(extension) and extension != link:
                    link = link[:-len(extension)]
        else:
            logger.warning("No link for name {} and language {} found".format(url, language))
        return link

    def scss(self, filename):
        return filename

    def load(self, src):
        o = urlparse(src)
        for loader_params in self.settings['loaders']:
            if loader_params['scheme'] == o.scheme:
                break
        else:
            raise TypeError("No loader for scheme: {}".format(o.scheme))
        loader = loader_params['loader'](self)
        path = src[len(o.scheme)+3:]
        return loader.load(path)

    def process(self, input, params, vars, language):
        for processor_params in self.settings['processors']:
            if params['type'] == processor_params['type']:
                break
        else:
            raise TypeError("No processor for file type: {}".format(filename))
        output = input
        full_vars = {
            'params' : params,
        }
        #first we include generic context
        full_vars.update(self.config.get('context', {}))
        #then language-specific context
        full_vars.update(self.config['languages'][language].get('context', {}))
        #then common definitions
        full_vars.update({
            'language' : self.config['languages'][language],
            'languages' : self.config['languages'],
            'lang' : language,
            'site' : self,
        })
        #then builder-specific variables
        full_vars.update(self.vars[language])
        #and finally variables passed as parameters
        full_vars.update(vars)
        for processor_cls in processor_params['processors']:
            processor = processor_cls(self, params, language)
            output = processor.process(output, full_vars)
        return output

    def get_filename(self, language, name):
        return self.links[language][name]

    def get_link(self, language, name):
        try:
            return '{}{}'.format(self.path, self.get_filename(language, name))
        except KeyError:
            return None

    def request(self, name, *args, **kwargs):
        if not name in self.providers:
            raise ValueError("No provider of type {} found!".format(name))
        return self.providers[name](*args, **kwargs)

    def init_builders(self):
        self.links = {}
        self.link_attrs = {}
        self.vars = {}
        self.providers = {}
        self.addons = defaultdict(list)
        self.files = []
        self.builders = []

        for builder_config in self.settings['builders']:
            logging.info("Initializing builder {}...".format(builder_config['name']))
            builder_class = builder_config['builder']
            if isinstance(builder_class, str):
                components = builder_class.split('.')
                builder_module = '.'.join(components[:-1])
                builder_class_str = components[-1]
                try:
                    module = importlib.import_module(builder_module)
                    builder_class = getattr(module, builder_class_str)
                except ImportError:
                    raise
            builder = builder_class(self)
            self.providers.update(builder.providers)
            if builder.addons:
                for key, addon in builder.addons.items():
                    self.addons[key].append(addon)
            self.builders.append(builder)

    def build(self):

        self.init_builders()

        for language, params in self.config.get('languages', {}).items():
            self.links[language] = {}
            self.link_attrs[language] = {}
            self.vars[language] = {}
            for builder in self.builders:
                params['name'] = language
                #here the builders create links and other structures
                result = builder.index(params, language)
                self.links[language].update(result.get('links', {}))
                self.link_attrs[language].update(result.get('link_attrs', {}))
                self.vars[language].update(result.get('vars', {}))

        for builder in self.builders:
            #now the builder "build" their components
            builder.build()

        for builder in self.builders:
            #now builders can do some post-processing
            builder.postprocess()
