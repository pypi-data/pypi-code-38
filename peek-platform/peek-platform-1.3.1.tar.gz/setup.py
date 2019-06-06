import os
import shutil
from setuptools import setup

from setuptools import find_packages

from peek_platform.WindowsPatch import isWindows

pip_package_name = "peek-platform"
py_package_name = "peek_platform"
package_version = '1.3.1'

egg_info = "%s.egg-info" % pip_package_name
if os.path.isdir(egg_info):
    shutil.rmtree(egg_info)

if os.path.isfile('MANIFEST'):
    os.remove('MANIFEST')

# pip install flower==0.7.3 tornado==3.2.2


requirements = [
    # packages used for the platform to test and upgrade it's self
    "pip >= 9.0.0",
    "setuptools >= 18.0.0",
    "virtualenv >= 15.1.0",

    # networking and async framework. Peek is based on Twisted.
    "Cython >= 0.21.1",
    "Twisted[tls,conch] < 19.0.0",
    "pyOpenSSL >= 16.2.0",
    "pyasn1 >= 0.1.9",
    "pyasn1-modules >= 0.0.8",

    # Database
    "psycopg2-binary >= 2.7.6",  # PostGreSQL for Linux
    "SQLAlchemy >= 1.0.14",  # Database abstraction layer
    "SQLAlchemy-Utils >= 0.32.9",
    "alembic >= 0.8.7",  # Database migration utility
    # installed and configured first

    # Utilities
    "python-dateutil >= 2.6.0",
    "Pygments >= 2.0.1",  # Generate HTML for code that is syntax styled
    "watchdog >= 0.8.3", # Used to detect file changes and re-copy them for frontend builds

    # Licensing
    "pycryptodome",

    # Celery packages
    "flower",
    # "amqp >= 1.4.9",  # DEPENDENCY LINK BELOW
    "redis >= 2.10.5",

    # Potentially useful packages
    # "GitPython >= 2.0.8",
    # "jira",
    # "dxfgrabber >= 0.7.4",

    # Peek platform dependencies, all must match
    "peek-plugin-base",  ##==%s" % py_package_name,
    "peek-core-device",  ##==%s" % py_package_name,
    "peek-core-email"  ##==%s" % py_package_name,
]

lin_dependencies = [
    # We still require shapely on windows, but we need to manually download the win wheel
    "Shapely >= 1.5.16",  # Geospatial shape manipulation

    # We still require pymssql on windows, but we need to manually download the win wheel
    "pymssql",

    # Celery 4 is not supported on windows
    "celery[redis,auth]",
]

win_dependencies = [
    # "pymssql >= 2.1.3",  # DB-API interface to Microsoft SQL Server, requires FreeTDS
    "pycparser >= 2.17",
    "cffi >= 1.9.1",
    "cryptography >= 1.7.1",
    "pytest >= 3.0.5",
    "wheel >= 0.30.0a0",
    "virtualenv >= 15.1.0",

    # Celery 4 is not supported on windows
    "celery[redis,auth]<4.0.0",

    # Service support for windows
    "pypiwin32"
]

if isWindows:
    requirements.extend(win_dependencies)

else:
    requirements.extend(lin_dependencies)

# Packages that are presently installed from a git repo
# See http://stackoverflow.com/questions/17366784/setuptools-unable-to-use-link-from-dependency-links/17442663#17442663
dependency_links = [
    # Celery packages
    # "git+https://github.com/celery/py-amqp#egg=amqp",

]

dev_requirements = [
    "coverage >= 4.2",
    "mock >= 2.0.0",
    "selenium >= 2.53.6",
]

requirements.extend(dev_requirements)

setup(
    name=pip_package_name,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'winsvc_peek_restarter = peek_platform.winsvc_peek_restarter:main',
        ],
    },
    dependency_links=dependency_links,
    process_dependency_links=True,
    zip_safe=False,version=package_version,
    description='Peek Platform Common Code',
    author='Synerty',
    author_email='contact@synerty.com',
    url='https://github.com/Synerty/%s' % py_package_name,
    download_url='https://github.com/Synerty/%s/tarball/%s' % (
        pip_package_name, package_version),
    keywords=['Peek', 'Python', 'Platform', 'synerty'],
    classifiers=[
        "Programming Language :: Python :: 3.5",
    ],
)
