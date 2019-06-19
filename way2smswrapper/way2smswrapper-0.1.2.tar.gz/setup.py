# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['way2smswrapper']

package_data = \
{'': ['*']}

install_requires = \
['selenium>=3.141,<4.0', 'xvfbwrapper>=0.2.9,<0.3.0']

setup_kwargs = {
    'name': 'way2smswrapper',
    'version': '0.1.2',
    'description': 'A Python Messaging Module Using Way2SMS & Selenium Module.',
    'long_description': '# way2smswrapper\n<p>\n  <img src="https://img.shields.io/badge/version-0.1.2-blue.svg?cacheSeconds=2592000" />\n  <a href="https://github.com/probhakarroy/way2smswrapper#readme">\n    <img alt="Documentation" src="https://img.shields.io/badge/documentation-yes-brightgreen.svg" target="_blank" />\n  </a>\n  <a href="https://github.com/probhakarroy/way2smswrapper/graphs/commit-activity">\n    <img alt="Maintenance" src="https://img.shields.io/badge/Maintained%3F-yes-green.svg" target="_blank" />\n  </a>\n  <a href="https://github.com/probhakarroy/way2smswrapper/blob/master/LICENSE">\n    <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg" target="_blank" />\n  </a>\n</p>\n\n> A Python Messaging Module Using Way2SMS & Selenium Module.  \n> Created By $implic@\n\n## Install\n```sh\n$pip install way2smswrapper\n```\n\nRequirements :-\n\n               Python3.\n               Firefox Browser. \n               Geckodriver. \n               Xvfb - Installation. \n               Way2SMS Account.\n\nThe python module uses selenium module to control the firefox browser which is being controlled by geckodriver.\nThe module is using xvfb(x-virtual frame buffer) and the xvfb wrapper for python3 to run the firefox browser \nheadlessly(in the background). Way2SMS Account is being used to send the message to the desired mobile number.\n\nOne can import the module in his/her own python3 program to send the status of the current running program to \nthe user\'s mobile phone number through sms using the user\'s Way2SMS Account.\n\n## Usage   :-\n```sh          \nimport w2swrapper\n```\n\n## Methods : \n```sh          \nwrapper.login()\nwrapper.sms(\'Message\')\n```\n\nTested In Ubuntu-17.04\n',
    'author': 'Probhakar Roy',
    'author_email': 'probhakarroy3110@gmail.com',
    'url': 'https://github.com/probhakarroy/way2smswrapper',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
