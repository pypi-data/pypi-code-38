from .conf import get_setting

__title__ = 'fobi.contrib.plugins.form_elements.fields.' \
            'hidden_model_object.settings'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2014-2019 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('IGNORED_MODELS',)

IGNORED_MODELS = get_setting('IGNORED_MODELS')
