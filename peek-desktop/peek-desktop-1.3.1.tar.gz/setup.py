import os
import shutil
import subprocess
from subprocess import CalledProcessError

from setuptools import setup, find_packages

pip_package_name = "peek-desktop"
py_package_name = "peek_desktop"

package_version = '1.3.1'

egg_info = "%s.egg-info" % pip_package_name
if os.path.isdir(egg_info):
    shutil.rmtree(egg_info)

if os.path.isfile('MANIFEST'):
    os.remove('MANIFEST')

excludePathContains = ('__pycache__', 'node_modules', 'platforms', 'dist')
excludeFilesEndWith = ('.pyc', '.js', '.js.map', '.lastHash')
excludeFilesStartWith = ('peek_plugin', 'peek_core')
includeFilesStartWith = ('webpack.config.js', 'karma.conf.js', 'protractor.conf.js')


def find_package_files():
    paths = []
    for (path, directories, filenames) in os.walk(py_package_name):
        if [e for e in excludePathContains if e in path]:
            continue

        for filename in filenames:
            if not [e for e in includeFilesStartWith if filename.startswith(e)]:
                if [e for e in excludeFilesEndWith if filename.endswith(e)]:
                    continue

                if [e for e in excludeFilesStartWith if filename.startswith(e)]:
                    continue

            relPath = os.path.join(path, filename)
            try:
                subprocess.check_call(['git', 'check-ignore', '-q', relPath])

            except CalledProcessError:
                paths.append(relPath[len(py_package_name) + 1:])

    return paths


package_files = find_package_files()

setup(
    name=pip_package_name,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_data={'': package_files},
    install_requires=[],
    zip_safe=False, version=package_version,
    description='Peek Platform - desktop Service (Frontend)',
    author='Synerty',
    author_email='contact@synerty.com',
    url='https://github.com/Synerty/%s' % pip_package_name,
    download_url='https://github.com/Synerty/%s/tarball/%s' % (
        pip_package_name, package_version),
    keywords=['Peek', 'Python', 'Platform', 'synerty'],
    classifiers=[
        "Programming Language :: Python :: 3.6",
    ],
)
