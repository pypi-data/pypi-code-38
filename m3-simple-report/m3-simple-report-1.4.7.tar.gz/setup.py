# coding: utf-8
import os
from setuptools import setup, find_packages


setup(
    name='m3-simple-report',
    description=u'Генератор отчетов',
    url='https://stash.bars-open.ru/projects/M3/repos/simple-report',
    license='MIT',
    author='BARS Group',
    author_email='bars@bars-open.ru',
    classifiers=[
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Natural Language :: Russian',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=(
        'xlwt',
        'xlrd',
        'xlutils',
        'lxml',
    ),
    include_package_data=True,
    dependency_links=(
        'http://pypi.bars-open.ru/simple/m3-builder',
    ),
    setup_requires=(
        'm3-builder>=1.2',
    ),
    set_build_info=os.path.dirname(__file__),
)
