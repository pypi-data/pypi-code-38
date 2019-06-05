# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['blender_basico']

package_data = \
{'': ['*'],
 'blender_basico': ['static/blender_basico/assets_shared/*',
                    'static/blender_basico/assets_shared/fonts/*',
                    'static/blender_basico/assets_shared/images/*',
                    'static/blender_basico/assets_shared/js/*',
                    'static/blender_basico/assets_shared/js/min/*',
                    'static/blender_basico/assets_shared/scripts/tutti/*',
                    'static/blender_basico/assets_shared/styles/*',
                    'static/blender_basico/assets_shared/templates/*',
                    'static/blender_basico/js/tutti/*',
                    'static/blender_basico/js/vendor/*',
                    'static/blender_basico/styles/*',
                    'static/blender_basico/styles/vendor/bootstrap/scss/*',
                    'static/blender_basico/styles/vendor/bootstrap/scss/mixins/*',
                    'static/blender_basico/styles/vendor/bootstrap/scss/utilities/*',
                    'static/blender_basico/styles/vendor/bootstrap/scss/vendor/*',
                    'templates/blender_basico/*']}

install_requires = \
['django-pipeline>=1.6,<2.0',
 'django>=2.2,<3.0',
 'jsmin>=2.2,<3.0',
 'libsasscompiler>=0.1.5,<0.2.0',
 'pypugjs>=5.8,<6.0']

setup_kwargs = {
    'name': 'blender-basico',
    'version': '0.1.1',
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
