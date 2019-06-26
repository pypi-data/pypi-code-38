"""
Hyckle
--------------
A memory-friendly warpper of pickle with better compression.
"""
import re
from setuptools import setup

with open('hyckle.py', 'rb') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        f.read().decode(), re.MULTILINE).group(1)

setup(
    name='hyckle',
    version=version,
    url='https://github.com/zylo117/Hyckle/',
    license='GPL-3.0',
    author='zylo117',
    author_email='zylo117@hotmail.com',
    description='A memory-friendly warpper of pickle with better compression.',
    long_description=__doc__,
    py_modules=['hyckle'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Database',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)