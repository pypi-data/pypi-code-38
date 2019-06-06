import os
import sys
import setuptools
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setuptools.setup(name='yoctopuce',
      version='1.10.35652',
      packages=['yoctopuce'],
      description="Yoctopuce python API",
      long_description=long_description,
      long_description_content_type='text/markdown',
      author="Yoctopuce",
      author_email="support@yoctopuce.com",
      url="https://www.yoctopuce.com",
      include_package_data=True,
      keywords='Yoctopuce USB sensors actuators API',
      project_urls={
          'Documentation': 'https://www.yoctopuce.com/EN/doc/reference/yoctolib-python-EN.html',
          'Source': 'https://github.com/yoctopuce/yoctolib_python'
      },
      zip_safe=False,
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Customer Service',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'Natural Language :: English',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows :: Windows XP',
          'Operating System :: Microsoft :: Windows :: Windows Server 2008',
          'Operating System :: Microsoft :: Windows :: Windows Vista',
          'Operating System :: Microsoft :: Windows :: Windows 7',
          'Operating System :: Microsoft :: Windows :: Windows 8',
          'Operating System :: Microsoft :: Windows :: Windows 8.1',
          'Operating System :: Microsoft :: Windows :: Windows 10',
          'Operating System :: Unix',
          'Operating System :: Unix',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.0',
          'Programming Language :: Python :: 3.1',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7'])
