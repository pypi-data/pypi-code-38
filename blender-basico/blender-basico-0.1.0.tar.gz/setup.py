# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['blender_basico']

package_data = \
{'': ['*'],
 'blender_basico': ['static/assets_shared/*',
                    'static/assets_shared/fonts/*',
                    'static/assets_shared/images/*',
                    'static/assets_shared/js/*',
                    'static/assets_shared/js/min/*',
                    'static/assets_shared/scripts/tutti/*',
                    'static/assets_shared/styles/*',
                    'static/assets_shared/templates/*',
                    'static/js/tutti/*',
                    'static/js/vendor/*',
                    'static/styles/*',
                    'static/styles/vendor/bootstrap/scss/*',
                    'static/styles/vendor/bootstrap/scss/mixins/*',
                    'static/styles/vendor/bootstrap/scss/utilities/*',
                    'static/styles/vendor/bootstrap/scss/vendor/*',
                    'templates/blender_basico/*']}

install_requires = \
['django-pipeline>=1.6,<2.0',
 'django>=2.2,<3.0',
 'jsmin>=2.2,<3.0',
 'libsasscompiler>=0.1.5,<0.2.0',
 'pypugjs>=5.8,<6.0']

setup_kwargs = {
    'name': 'blender-basico',
    'version': '0.1.0',
    'description': 'Django shared app, featuring essential components for blender.org sites.',
    'long_description': None,
    'author': 'Francesco Siddi',
    'author_email': 'francesco@blender.org',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
