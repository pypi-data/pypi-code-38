import os
from io import open
from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), "r", encoding="utf-8") as fobj:
    long_description = fobj.read()

requires = [
    "six>=1.12.0",
    "click",
    "psutil",
]

setup(
    name="checkalive",
    version="0.1.9",
    description="检查系统状态，如：指定的IP地址是否存在，指定的端口是否被监听，指定的进程是否存活。",
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