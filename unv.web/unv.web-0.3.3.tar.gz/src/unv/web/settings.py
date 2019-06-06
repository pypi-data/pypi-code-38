import copy

import jinja2

from unv.app.settings import ComponentSettings, SETTINGS as APP_SETTINGS


class WebSettings(ComponentSettings):
    KEY = 'web'
    SCHEMA = {
        'autoreload': {'type': 'boolean', 'required': True},
        'jinja2': {
            'type': 'dict',
            'required': True,
            'schema': {'enabled': {'type': 'boolean'}}
        },
        'link_static': {'type': 'boolean', 'required': True}
    }
    DEFAULT = {
        'autoreload': False,
        'link_static': True,
        'jinja2': {'enabled': True},
    }

    @property
    def link_static(self):
        return self._data['link_static']

    @property
    def jinja2_enabled(self):
        return self._data['jinja2']['enabled']

    @property
    def jinja2_settings(self):
        settings = copy.deepcopy(self._data.get('jinja2', {}))
        settings.pop('enabled')
        settings['enable_async'] = True
        settings['loader'] = jinja2.ChoiceLoader([
            jinja2.PackageLoader(component.__name__)
            for component in APP_SETTINGS.get_components()
        ])
        if 'jinja2.ext.i18n' not in settings.setdefault('extensions', []):
            settings['extensions'].append('jinja2.ext.i18n')
        return settings


SETTINGS = WebSettings()
