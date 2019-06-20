import os
from io import open
from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), "r", encoding="utf-8") as fobj:
    long_description = fobj.read()

requires = [
    "click",
    "psutil",
]

setup(
    name="checkalive",
    version="0.1.1",
    description="Check system status.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/appstore-zencore/checkalive",
    author="zencore",
    author_email="dobetter@zencore.cn",
    license="MIT",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords=['openpyxl', 'xlsx split', 'excel split'],
    requires=requires,
    install_requires=requires,
    packages=find_packages("."),
    py_modules=["checkalive"],
    entry_points={
        'console_scripts': [
            'checkalive = checkalive:main',
            'checkip = checkalive:cmd_checkip',
            'checkport = checkalive:cmd_checkport',
            'checkproc = checkalive:cmd_checkproc',
        ]
    },
)