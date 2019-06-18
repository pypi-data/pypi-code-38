import os
from io import open
from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), "r", encoding="utf-8") as fobj:
    long_description = fobj.read()

requires = [
    "openpyxl",
    "xlsxhelper",
]

setup(
    name="xlsx-split",
    version="0.1.0",
    description="Excel表格分割工具。",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/appstore-zencore/xlsx-split",
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
    py_modules=["xlsx_split"],
    entry_points={
        'console_scripts': ['xlsx-split = xlsx_split:main']
    },
)