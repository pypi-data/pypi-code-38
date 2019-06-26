import re
from os.path import join, dirname
from setuptools import setup, find_packages

# Reading package's version
with open(join(dirname(__file__), 'linkable', '__init__.py')) as v_file:
    version = re.compile(r".*__version__ = '(.*?)'", re.S).match(
        v_file.read()
    ).group(1)

setup(
    name='linkable',
    version=version,
    author='Mahdi Ghane.g',
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(),
    description='Detect URL, Email, Hashtag and Mention from '
                'plain-text and convert into HTML hyperlink.',
    long_description=open('README.rst').read(),
    url='https://github.com/meyt/linkable-py',
    license='MIT License',
    classifiers=[
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Markup :: HTML'
    ]
)
