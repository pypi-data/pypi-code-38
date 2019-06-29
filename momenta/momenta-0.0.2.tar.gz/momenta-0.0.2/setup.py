#!/usr/bin/env python
# -*- coding: utf-8 -*

from setuptools import setup, find_packages, Command
import os

class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')


install_requires = [
    'itchat==1.3.10', 'pymongo==3.8.0', 'schedule==0.6.0', 'Click==7.0',
]


setup(
      version='0.0.2',
      name='momenta',
      author='ChengTian',
      description='',
      long_description='',
      entry_points={
        "console_scripts": ["momenta=pkg.cmd.cli:cli"]
      },
      url='https://github.com/Chengyumeng/momenta',
      author_email='792400644@qq.com',
      packages=find_packages(),
      include_package_data=True,
      license='MIT License',
      zip_safe=False,
      install_requires=install_requires,
      classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Programming Language :: Python :: 3.4',
      ],
      cmdclass={
            'clean': CleanCommand,
      },

)
