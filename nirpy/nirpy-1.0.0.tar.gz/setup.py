"""
#Module Created by LimerBoy with Love <3

* nircmdc: https://www.nirsoft.net/utils/nircmd.html
* nircmdc reference: https://nircmd.nirsoft.net

> Example usage:

import nirpy
nirpy.load()
nirpy.execute('monitor off')

Wait until all commands are executed and continue to execute your code.
nirpy.execute('infobox "Computer will restart" "INFO" && shutdown.exe -r -t 3600', wait=True)

Wait until command are executed with high process priority and continue to execute your code.
Process priority: [LOW | NORMAL | HIGH | REALTIME]
nirpy.execute('savescreenshotfull desktop.png', wait=True, priority='HIGH')

Download file from internet.
file = nirpy.wget(link)

Execute downloaded file.
nirpy.start(file)

after executing you can use: nirpy.unload() to remove nircmdc.exe from system.
"""

from setuptools import setup, find_packages

setup(name='nirpy',
      version='1.0.0',
      description='Use nircmdc commands in python',
      long_description='## Full description here: https://github.com/LimerBoy/nirpy/blob/master/README.md',
      url='https://github.com/LimerBoy/nirpy',
      author='LimerBoy',
      author_email='LimerBoyTV@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'wget',
      ],
      include_package_data=True,
      zip_safe=False)