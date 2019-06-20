# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['blender_basico']

package_data = \
{'': ['*'],
 'blender_basico': ['static/blender_basico/fonts/*',
                    'static/blender_basico/images/*',
                    'static/blender_basico/scripts/tutti/*',
                    'static/blender_basico/scripts/vendor/bootstrap-4.3.1.min.js',
                    'static/blender_basico/scripts/vendor/bootstrap-4.3.1.min.js',
                    'static/blender_basico/scripts/vendor/bootstrap-4.3.1.min.js',
                    'static/blender_basico/scripts/vendor/bootstrap-4.3.1.min.js',
                    'static/blender_basico/scripts/vendor/jquery-3.4.0.min.js',
                    'static/blender_basico/scripts/vendor/jquery-3.4.0.min.js',
                    'static/blender_basico/scripts/vendor/jquery-3.4.0.min.js',
                    'static/blender_basico/scripts/vendor/jquery-3.4.0.min.js',
                    'static/blender_basico/scripts/vendor/js.cookie-2.2.0.min.js',
                    'static/blender_basico/scripts/vendor/js.cookie-2.2.0.min.js',
                    'static/blender_basico/scripts/vendor/js.cookie-2.2.0.min.js',
                    'static/blender_basico/scripts/vendor/js.cookie-2.2.0.min.js',
                    'static/blender_basico/scripts/vendor/popper-1.15.0.min.js',
                    'static/blender_basico/scripts/vendor/popper-1.15.0.min.js',
                    'static/blender_basico/scripts/vendor/popper-1.15.0.min.js',
                    'static/blender_basico/scripts/vendor/popper-1.15.0.min.js',
                    'static/blender_basico/styles/*',
                    'static/blender_basico/styles/bootstrap/*',
                    'static/blender_basico/styles/bootstrap/mixins/*',
                    'static/blender_basico/styles/bootstrap/utilities/*',
                    'static/blender_basico/styles/bootstrap/vendor/*',
                    'templates/blender_basico/*']}

install_requires = \
['django-pipeline>=1.6,<2.0',
 'django>=2.2,<3.0',
 'jsmin>=2.2,<3.0',
 'libsasscompiler>=0.1.5,<0.2.0',
 'pypugjs>=5.8,<6.0']

entry_points = \
{'console_scripts': ['update-bwa = tools:update']}

setup_kwargs = {
    'name': 'blender-basico',
    'version': '0.1.3',
    'description': 'Django shared app, featuring essential components for blender.org sites.',
    'long_description': None,
    'author': 'Francesco Siddi',
    'author_email': 'francesco@blender.org',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
