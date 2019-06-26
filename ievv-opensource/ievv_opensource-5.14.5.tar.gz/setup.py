import json
import os
from setuptools import setup, find_packages


with open(os.path.join(os.path.dirname(__file__), 'ievv_opensource', 'version.json')) as f:
    version = json.loads(f.read())


setup(
    name='ievv_opensource',
    description='The opensource modules from the commercial IEVV Django framework.',
    version=version,
    author='Espen Angell Kristiansen, Tor Johansen, Magne Westlie',
    author_email='post@appresso.no',
    license='BSD',
    packages=find_packages(exclude=['manage']),
    install_requires=[
        'sh',
        'Django',
        'django_dbdev>=1.0.0',
        'django_cradmin>=1.1.1',
        'watchdog',
        'termcolor',
        'psutil',
        'future',
        'arrow',
    ],
    entry_points={
        'console_scripts': [
            'ievv = ievv_opensource.ievvtasks_common.cli:cli',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ]
)
