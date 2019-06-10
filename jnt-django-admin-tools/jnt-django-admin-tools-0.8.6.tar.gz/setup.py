# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['admin_tools',
 'admin_tools.dashboard',
 'admin_tools.dashboard.management',
 'admin_tools.dashboard.management.commands',
 'admin_tools.dashboard.migrations',
 'admin_tools.dashboard.templatetags',
 'admin_tools.fields',
 'admin_tools.menu',
 'admin_tools.menu.management',
 'admin_tools.menu.management.commands',
 'admin_tools.menu.migrations',
 'admin_tools.menu.templatetags',
 'admin_tools.services',
 'admin_tools.static.admin_tools.css',
 'admin_tools.static.admin_tools.css.widgets',
 'admin_tools.templates',
 'admin_tools.templates.admin_tools',
 'admin_tools.templatetags',
 'admin_tools.theming',
 'admin_tools.theming.templatetags',
 'admin_tools.widgets']

package_data = \
{'': ['*'],
 'admin_tools': ['locale/ar/LC_MESSAGES/*',
                 'locale/bg/LC_MESSAGES/*',
                 'locale/bn/LC_MESSAGES/*',
                 'locale/ca/LC_MESSAGES/*',
                 'locale/cs/LC_MESSAGES/*',
                 'locale/da/LC_MESSAGES/*',
                 'locale/de/LC_MESSAGES/*',
                 'locale/el/LC_MESSAGES/*',
                 'locale/en/LC_MESSAGES/*',
                 'locale/es/LC_MESSAGES/*',
                 'locale/es_AR/LC_MESSAGES/*',
                 'locale/fi/LC_MESSAGES/*',
                 'locale/fr/LC_MESSAGES/*',
                 'locale/he/LC_MESSAGES/*',
                 'locale/hu/LC_MESSAGES/*',
                 'locale/it/LC_MESSAGES/*',
                 'locale/ja/LC_MESSAGES/*',
                 'locale/nl/LC_MESSAGES/*',
                 'locale/pl/LC_MESSAGES/*',
                 'locale/pt/LC_MESSAGES/*',
                 'locale/pt_BR/LC_MESSAGES/*',
                 'locale/ru/LC_MESSAGES/*',
                 'locale/sk/LC_MESSAGES/*',
                 'locale/sv/LC_MESSAGES/*',
                 'locale/tr/LC_MESSAGES/*',
                 'locale/uk/LC_MESSAGES/*',
                 'locale/zh_CN/LC_MESSAGES/*',
                 'locale/zh_TW/LC_MESSAGES/*',
                 'static/admin_tools/images/*',
                 'static/admin_tools/js/*',
                 'static/admin_tools/js/jquery/*'],
 'admin_tools.dashboard': ['static/admin_tools/css/*',
                           'static/admin_tools/css/jquery/*',
                           'static/admin_tools/css/jquery/images/*',
                           'static/admin_tools/js/*',
                           'static/admin_tools/js/jquery/*',
                           'templates/admin/*',
                           'templates/admin_tools/dashboard/*',
                           'templates/admin_tools/dashboard/modules/*'],
 'admin_tools.menu': ['static/admin_tools/css/*',
                      'static/admin_tools/js/*',
                      'templates/admin/*',
                      'templates/admin_tools/menu/*'],
 'admin_tools.templates.admin_tools': ['widgets/*'],
 'admin_tools.theming': ['static/admin_tools/css/*',
                         'static/admin_tools/images/*',
                         'templates/admin/*']}

install_requires = \
['django>=2.0.0,<3.0.0']

setup_kwargs = {
    'name': 'jnt-django-admin-tools',
    'version': '0.8.6',
    'description': 'A collection of tools for the django administration interface',
    'long_description': None,
    'author': 'Junte',
    'author_email': 'tech@junte.it',
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
