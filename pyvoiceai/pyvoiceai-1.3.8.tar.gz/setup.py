# -*- coding: utf-8 -*-
import os
import sys

from setuptools import setup

description = "VoiceaiTech Python SDK"
about = open("./Log.txt", "rb").read().decode("utf-8", "ignore")
# print(about)

Version = '1.3.8'


def git_push():
    os.system('git add --all')
    os.system('git commit -m \"setup python dodo:v%s\"' % Version)
    os.system("git tag -d v%s" % Version)
    os.system("git tag v%s" % Version)
    os.system("git push origin :refs/tags/v%s" % Version)
    os.system("git push")
    os.system("git push --tags")


# 'setup.py publish' shortcut.
if sys.argv[-1] == 'publish':
    git_push()
    # pip install wheel
    os.system("rm -rf dist/*")
    os.system('python setup.py sdist bdist_wheel')
    # pip install twine
    os.system('twine upload dist/* --verbose')
    sys.exit()

if sys.argv[-1] == 'test':
    os.system('python setup.py develop')
    sys.exit()

if sys.argv[-1] == 'git':
    git_push()
    sys.exit()

packages = ['pyvoiceai']

requires = [
    'requests>=2.19.1',
    'pycryptodomex>=3.6.6',
    "pyOpenSSL>=18.0.0",
    "ws4py>=0.5.1"
]

setup(
    name='pyvoiceai',  # 应用名
    version=Version,  # 版本号
    author="voiceai",
    author_email="voiceai-github@voiceaitech.com",
    url="https://pypi.org/project/pyvoiceai/",
    description=description,
    long_description=about,
    license="",
    packages=packages,
    package_dir={packages[0]: 'pyvoiceai'},
    platforms=['any'],
    install_requires=requires,
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
)
