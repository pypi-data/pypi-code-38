from setuptools import setup
from setuptools import find_packages

setup(name='vshock',
      version='0.1.1',
      url='https://github.com/takagiy/vshock',
      description=
      'Generating fake input stream of duakshock 3 without real dualshock 3.',
      author='takagiy',
      author_email='takagiy.4dev@gmail.com',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      install_requires=['docopt', 'tornado'],
      entry_points={'console_scripts': ['vshock = vshock.cli:main']})
