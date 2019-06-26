from jinja2 import Environment, BaseLoader, TemplateNotFound
from algonaut.settings import settings
from urllib.parse import urlencode
import os

class TemplateLoader(BaseLoader):

    def __init__(self, paths):
        self.paths = paths

    def get_source(self, environment, template):
        for key, path in sorted(self.paths.items(), key=lambda x:x[0]):
            template_path = os.path.join(path, template)
            if not os.path.exists(template_path):
                continue
            mtime = os.path.getmtime(template_path)
            with open(template_path) as f:
                source = f.read()
            return source, template_path, lambda: mtime == os.path.getmtime(path)

        raise TemplateNotFound(template)

def jinja_email(template_path, context, version, language=None):

    base_url = settings.get('email.url')
    paths = settings.get('email.paths')[version]

    lang = language
    if lang is None:
        lang = settings.get('language', 'en')

    def get_url(path, query=None):
        querystring = ''
        if query:
            querystring = '?'+urlencode(query)
        return '{}/{}{}'.format(base_url, paths[path], querystring)

    def translate(key, language=None, *args, **kwargs):
        return settings.translate(language or lang, key, *args, **kwargs)

    #we set up the jinja environment with the template directories
    template_paths = settings.get('email.template_paths')
    jinja_env = Environment(loader=TemplateLoader(template_paths))
    jinja_env.filters['translate'] = translate
    jinja_env.filters['url'] = get_url

    c = {
        'language' : lang,
        'version' : version,
    }

    c.update(settings.get('email.context'))
    c.update(context)

    template = jinja_env.get_template(template_path)
    module = template.make_module(c)
    return module