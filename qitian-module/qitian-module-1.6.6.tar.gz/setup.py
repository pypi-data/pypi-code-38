#!/usr/bin/env python
from setuptools import setup, find_packages
import os
import sys

version = '1.6.6'

long_description = "\n".join([
    open('README.md', 'r').read(),
])

if sys.argv[-1] == 'build':
    os.system('rm -rf build dist *.egg-info')
    os.system('python setup.py sdist bdist_wheel')
    sys.exit()

if sys.argv[-1] == 'clear':
    os.system('rm -rf build dist *.egg-info django.log')
    sys.exit()

if sys.argv[-1] == 'publish':
    os.system('rm -rf build dist *.egg-info django.log')
    os.system('python setup.py sdist bdist_wheel')
    os.system('twine upload dist/*')
    sys.exit()

if sys.argv[-1] == 'tag':
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()


setup(
    name='qitian-module',
    description=(
        '起田(苏州)营销策划有限公司Django项目公用底层框架.'
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='framework qitian common module',
    version=version,
    author='Peter Han',
    author_email='peter@qitian.com',
    url='https://gitee.com/qtch/django_module',
    license='MIT License',
    packages=find_packages(include=['autopost', 'system', 'usercenter']),
    include_package_data=True,
    install_requires=[
        'django',
        'beautifulsoup4==4.6.0',
        # 'django-environ==0.4.5',
        'django-redis==4.9.0',
        'django-smart-selects==1.5.3',
        'django-uuslug==1.1.8',
        'shortuuid==0.5.0',
        'qiniu==7.2.2',
        'textrank4zh==0.3',
        'yunpian-python-sdk==1.0.0',
        'pycryptodomex==3.6.6',
        'python-crontab==2.3.5',
        'mammoth==1.4.8',
        'django-taggit==0.23.0',
        'django-comments-xtd',
        'awesome-slugify',
        'djangorestframework',
        'django-taggit-labels',
        'django-taggit-helpers',
        'PyMySQL',
    ],
    python_requires=">=3.6, !=3.0.*",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        'Topic :: Utilities',
    ],
    zip_safe=False,
)
