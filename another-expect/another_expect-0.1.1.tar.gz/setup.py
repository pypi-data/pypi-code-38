# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['another_expect',
 'another_expect._vendor',
 'another_expect._vendor.simple_chalk',
 'another_expect._vendor.simple_chalk.src',
 'another_expect._vendor.simple_chalk.src.utils',
 'another_expect._vendor.simple_chalk.src.utils.internal',
 'another_expect._vendor.simple_chalk.tests',
 'another_expect._vendor.tedent',
 'another_expect._vendor.tedent._vendor',
 'another_expect._vendor.tedent._vendor.wrapt',
 'another_expect._vendor.tedent.fns',
 'another_expect._vendor.tedent.fns.decorators',
 'another_expect._vendor.tedent.fns.internal',
 'another_expect._vendor.wrapt',
 'another_expect.expect',
 'another_expect.expect.to',
 'another_expect.expect.to.be',
 'another_expect.fns',
 'another_expect.fns.decorators',
 'another_expect.fns.internal']

package_data = \
{'': ['*'],
 'another_expect._vendor': ['ordered_set-3.1.1.dist-info/*',
                            'simple_chalk-0.1.0.dist-info/*',
                            'tedent-0.1.5.dist-info/*',
                            'wrapt-1.11.1.dist-info/*'],
 'another_expect._vendor.tedent._vendor': ['ordered_set-3.1.1-py3.7.egg-info/*',
                                           'wrapt-1.11.1.dist-info/*']}

setup_kwargs = {
    'name': 'another-expect',
    'version': '0.1.1',
    'description': 'An expect function with an api and documentation to my liking',
    'long_description': '## Another Expect\n\nThis module is not ready for public use.\n',
    'author': 'Philip Olson',
    'author_email': 'philip.olson@pm.me',
    'url': 'https://github.com/olsonpm/py_simple-test',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
