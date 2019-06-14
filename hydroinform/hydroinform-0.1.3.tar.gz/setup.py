import setuptools
import os
import sys

_here = os.path.abspath(os.path.dirname(__file__))

if sys.version_info[0] < 3:
    with open(os.path.join(_here, 'README.md')) as f:
        long_description = f.read()
else:
    with open(os.path.join(_here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()


setuptools.setup(
    name="hydroinform",
    version="0.1.3",
    author="Jan Gregersen and Jacob Gudbjerg",
    author_email="jacobgudbjerg@gmail.com",
    description="A steady-state stream model and python access to DFS-files",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="http://hydroinform.dk",

    packages=setuptools.find_packages(include=['hydroinform']),
    install_requires=[
        'enum34;python_version<"3.4"',
        'pyshp>=2.1',
        'numpy',
        'matplotlib',
        'pythonnet'
        ],
    classifiers=(
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ),
)