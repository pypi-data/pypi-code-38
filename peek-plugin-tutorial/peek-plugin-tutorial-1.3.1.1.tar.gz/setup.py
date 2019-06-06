import os
import shutil
from setuptools import setup

from setuptools import find_packages

#
# Modify these values to fork a new plugin
#
author = "Synerty"
author_email = 'contact@synerty.com'
py_package_name = "peek_plugin_tutorial"
pip_package_name = py_package_name.replace('_', '-')
package_version = '1.3.1.1'
description = 'Peek Plugin Tutorial - My first enhancement.'

download_url = 'https://bitbucket.org/synerty/%s/get/%s.zip'
download_url %= pip_package_name, package_version
url = 'https://bitbucket.org/synerty/%s' % pip_package_name

#
# Everything below should be ok
#
egg_info = "%s.egg-info" % pip_package_name
if os.path.isdir(egg_info):
    shutil.rmtree(egg_info)

if os.path.isfile('MANIFEST'):
    os.remove('MANIFEST')

excludePathContains = ('__pycache__', 'node_modules', 'platforms', 'dist')
excludeFilesEndWith = ('.pyc', '.js', '.js.map', '.lastHash')
excludeFilesStartWith = ()


def find_package_files():
    paths = []
    for (path, directories, filenames) in os.walk(py_package_name):
        if [e for e in excludePathContains if e in path]:
            continue

        for filename in filenames:
            if [e for e in excludeFilesEndWith if filename.endswith(e)]:
                continue

            if [e for e in excludeFilesStartWith if filename.startswith(e)]:
                continue

            paths.append(os.path.join(path[len(py_package_name) + 1:], filename))

    return paths


package_files = find_package_files()

setup(
    name=pip_package_name,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_data={'': package_files},
    install_requires=['peek-plugin-base'],
    version=package_version,
    description=description,
    author=author,
    author_email=author_email,
    url=url,
    download_url=download_url,
    keywords=['Peek', 'Python', 'Platform', 'synerty'],
    classifiers=[],
)