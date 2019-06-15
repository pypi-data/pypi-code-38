from setuptools import setup, find_packages
import platform

cmdclass_dict = {}

install_requires = []

dev_requires = [
    'sniffer', 'coverage', 'mypy', 'twine',
    'wheel', 'nose', 'pytest']

makes_sniffer_scan_faster = {
    "Linux": "pyinotify",
    "Windows": "pywin32",
    "Darwin": "MacFSEvents"
}

if platform.system() in makes_sniffer_scan_faster:
    dev_requires.append(makes_sniffer_scan_faster[platform.system()])

def read_file(f):
    with open(f, "r") as fh:
        return fh.read()

long_description = read_file("README.md")

try:
    from hs_build_tools.setup import get_version_and_add_release_cmd
    version = get_version_and_add_release_cmd('version.txt', cmdclass_dict)
except ModuleNotFoundError:
    version = read_file('version.txt').strip()


setup(name='hs_build_tools',
      version=str(version),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Build Tools',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
      ],
      description='hashstore build tools',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/walnutgeek/hashstore',
      author='Walnut Geek',
      author_email='wg@walnutgeek.com',
      license='Apache 2.0',
      packages=find_packages(exclude=("tests",)),
      package_data={},
      cmdclass=cmdclass_dict,
      entry_points={},
      install_requires=install_requires,
      extras_require={'dev': dev_requires},
      zip_safe=True)