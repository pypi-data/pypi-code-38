#!/usr/bin/env python3

import os
import subprocess
import sys
from setuptools import setup


# NOTE: This file must remain Python 2 compatible for the foreseeable future,
# to ensure that we error out properly for people with outdated setuptools
# and/or pip.
if sys.version_info < (3, 4):
    error = """
Beginning with PyOCR 0.7, Python 3.4 or above is required.

This may be due to an out of date pip.

Make sure you have pip >= 9.0.1.
"""
    sys.exit(error)


if os.name == 'nt':
    setup_deps = []
    scm_version = {}
    # setuptools_scm doesn't work in MSYS2
    if not os.path.exists('src/pyocr/_version.py'):
        version = subprocess.run(
            'git describe --always',
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        version = version.stdout.decode("utf-8").strip()
        version = version.split("-")[0]

        with open('src/pyocr/_version.py', 'w') as fd:
            fd.write("version = '{}'\n".format(version))
    else:
        with open("src/pyocr/_version.py", "r") as fd:
            for line in fd.readlines():
                if line[0] != '#' and line.strip() != '':
                    version = line.strip()
                    version = version.split(" ")[2][1:-1]
                    break
else:
    setup_deps = [
        'setuptools_scm',
        'setuptools_scm_git_archive',
    ]
    scm_version = {
        'write_to': 'src/pyocr/_version.py',
    }
    version = None


setup(
    name="pyocr",
    description=("A Python wrapper for OCR engines (Tesseract, Cuneiform,"
                 " etc)"),
    keywords="tesseract cuneiform ocr",
    version=version,
    url="https://gitlab.gnome.org/World/OpenPaperwork/pyocr",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later"
        " (GPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Multimedia :: Graphics :: Capture :: Scanners",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Scientific/Engineering :: Image Recognition",
    ],
    license="GPLv3+",
    author="Jerome Flesch",
    author_email="jflesch@openpaper.work",
    packages=[
        'pyocr',
        'pyocr.libtesseract',
    ],
    package_dir={
        '': 'src',
    },
    data_files=[],
    scripts=[],
    zip_safe=True,
    python_requires='>=3.4',
    install_requires=[
        "Pillow",
    ],
    setup_requires=setup_deps,
    use_scm_version=scm_version,
)
