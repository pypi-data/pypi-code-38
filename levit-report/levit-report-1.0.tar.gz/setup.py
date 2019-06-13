import os
from setuptools import setup

# try:
#     import pypandoc
#
#     README = pypandoc.convert_file('README.md', 'rst')
# except ImportError:
#     with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
#         README = readme.read()
with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

__import__('pprint').pprint(README)

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='levit-report',
    version='1.0',
    packages=['levit_report', 'levit_report.migrations'],
    include_package_data=True,
    license='MIT License',  # example license
    description='Bring the power of relatorio to Django',
    long_description_content_type="text/markdown",
    long_description=README,
    url='http://levit.be',
    author='LevIT scs',
    author_email='foss@levit.be',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=['Django>=1.8', 'relatorio>=0.6.1', ]
)
