import sys
from setuptools import setup, find_packages

install_requires = ['requests']
if sys.version_info < (3, 4):
    install_requires.append('enum34')

setup(
    name = 'netbluemind',
    packages = find_packages(),
    version = '3.1.41145',
    description = 'Automatically generated client for BlueMind < 4 REST API. Check netbluemind4 for more recent releases',
    author = 'BlueMind team',
    author_email = 'contact@bluemind.net',
    url = 'http://git.blue-mind.net/bluemind/',
    keywords = ['bluemind', 'rest', 'api', 'mail', 'groupware'],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    install_requires=install_requires
)
