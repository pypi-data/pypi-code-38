import os
import shutil
from setuptools import setup

from setuptools import find_packages

pip_package_name = "peek-plugin-base"
py_package_name = "peek_plugin_base"
package_version = '1.3.1'

egg_info = "%s.egg-info" % pip_package_name
if os.path.isdir(egg_info):
    shutil.rmtree(egg_info)

if os.path.isfile('MANIFEST'):
    os.remove('MANIFEST')

requirements = [
    # Database packages
    "SQLAlchemy >= 1.0.14",  # Database abstraction layer
    "SQLAlchemy-Utils >= 0.32.9",
    "alembic >= 0.8.7",  # Database migration utility
    "GeoAlchemy2",  # Geospatial addons to SQLAlchemy


    # networking and async framework. Peek is based on Twisted.
    "Twisted[tls,conch] < 19.0.0",
    
    # Celery packages
    "txcelery-py3 >= 1.3.0",

    # The package for RW support
    "json-cfg-rw",
    
    # Protocol and data packages
    "pytmpdir >= 0.2.3",  # A temporary directory, useful for extracting archives to
    "txhttputil >= 0.2.7",  # Utility class for http requests
    "vortexpy >= 1.0.9",  # Data serialisation and transport layer, observable based

    # SOAP interface packages
    "SOAPpy-py3 >= 0.52.24",  # See http://soappy.ooz.ie for tutorials
    "wstools-py3 >= 0.54.2",
    "txsuds-py3 >= 0.5.9",

    # RxPY by Microsoft. Potentially used in plugins to create Observables.
    "rx >= 1.5.7",

    # Improve datetime support
    "pytz",
    "tzlocal"

]

# Packages that are presently installed from a git repo
dependency_links= [
]

setup(
    name=pip_package_name,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=requirements,
    dependency_links=dependency_links,
    zip_safe=False,version=package_version,
    description='Peek Plugin Base',
    author='Synerty',
    author_email='contact@synerty.com',
    url='https://github.com/Synerty/%s' % pip_package_name,
    download_url='https://github.com/Synerty/%s/tarball/%s' % (
        pip_package_name, package_version),
    keywords=['Peek', 'Python', 'Platform', 'synerty'],
    classifiers=[
        "Programming Language :: Python :: 3.5",
    ],
)
