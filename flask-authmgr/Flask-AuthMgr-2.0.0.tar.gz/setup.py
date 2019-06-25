#coding:utf-8
'''
* coder  : dzlua
* email  : 505544956@qq.com
* module : Flask-AuthMgr
* path   : .
* file   : setup.py
* time   : 2017-11-03 13:33:54
'''
#--------------------#
import re
from setuptools import setup

with open('flask_auth_mgr.py', 'r') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        f.read(), re.MULTILINE).group(1)

setup(
    name='Flask-AuthMgr',
    version=version,
    url='https://gitee.com/dzlua/Flask-AuthMgr.git',
    license='MIT',
    author='dzlua',
    author_email='505544956@qq.com',
    description='A flask extension based on Flask-HTTPAuth for managing restful API Auth.',
    py_modules=['flask_auth_mgr'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    keywords = ['Flask', 'Flask-AuthMgr', 'Flask-HTTPAuth', 'flask_httpauth', 'auth', 'flask_auth_mgr'],
    install_requires=[
        'Flask-HTTPAuth'
    ],
    test_suite="tests",
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)