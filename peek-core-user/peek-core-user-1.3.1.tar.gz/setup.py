import os
import shutil

from setuptools import find_packages
from setuptools import setup

pip_package_name = "peek-core-user"
py_package_name = "peek_core_user"

package_version = '1.3.1'

egg_info = "%s.egg-info" % pip_package_name
if os.path.isdir(egg_info):
    shutil.rmtree(egg_info)

if os.path.isfile('MANIFEST'):
    os.remove('MANIFEST')

excludePathContains = ('__pycache__', 'node_modules', 'platforms', 'dist')
excludeFilesEndWith = ('.pyc', '.js', '.js.map', '.lastHash')
excludeFilesStartWith = ()

dependencies = [
    'peek-plugin-base',
    'python-ldap'
]


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
    install_requires=dependencies,
    zip_safe=False, version=package_version,
    description='Peek Plugin - UserDb - This is the No Operation test/example plugin',
    author='Synerty',
    author_email='contact@synerty.com',
    url='https://github.com/Synerty/%s' % py_package_name,
    download_url='https://github.com/Synerty/%s/tarball/%s' % (
        pip_package_name, package_version),
    keywords=['Peek', 'Python', 'Platform', 'synerty'],
    classifiers=[],
)
