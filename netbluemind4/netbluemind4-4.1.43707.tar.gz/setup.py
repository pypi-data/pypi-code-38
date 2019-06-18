import sys
from setuptools import setup, find_packages

install_requires = ['requests']
if sys.version_info < (3, 4):
    install_requires.append('enum34')

setup(
    name = 'netbluemind4',
    packages = find_packages(),
    version = '4.1.43707',
    description = 'Automatically generated client for BlueMind >= 4 REST API. Check netbluemind for older releases',
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
