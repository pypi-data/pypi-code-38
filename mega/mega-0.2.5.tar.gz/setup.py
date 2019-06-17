import os
import sys
from codecs import open

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

# 'setup.py publish' shortcut
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_wheel')
    os.system('twine upload dist/*')
    sys.exit()

packages = ['mega']

requires = [
    'trio>=0.9.0',
    'asks>=2.2.0',
    'beautifulsoup4>=4.6.3',
    'lxml>=4.2.5',
    'requests>=2.21.0'
]

about = {}
with open(os.path.join(here, 'mega', '__version__.py'), 'r', 'utf-8') as f:
    exec(f.read(), about)

with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=readme,
    long_description_content_type='text/markdown',
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    license=about['__license__'],
    packages=packages,
    package_data={'': ['LICENSE']},
    # package_dir={'mega': 'mega'},
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=requires,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7'
    ],
    entry_points={
        'console_scripts': 'mega=mega.mega:main'
    },
)
