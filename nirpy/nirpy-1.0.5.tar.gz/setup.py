"""
#Module Created by LimerBoy with Love <3

* nircmdc: https://www.nirsoft.net/utils/nircmd.html
* nircmdc reference: https://nircmd.nirsoft.net

> Example usage:

import nirpy
nirpy.load() # if you pc is 64bit: nirpy.load(architecture=64)

# NIRCMDC.exe
nirpy.execute('monitor off')

# CMD.exe
nirpy.system('echo this is a system command!')

#Execute with high process priority
#Process priority: [LOW | NORMAL | HIGH | REALTIME]
nirpy.execute('savescreenshotfull desktop.png', priority='HIGH')

#Download file from internet.
file = nirpy.wget(link)

#Execute downloaded file.
nirpy.start(file)

#Add/Remove autorun
nirpy.autorun('C:\\Windows', 'notepad.exe', 'you_name', state=True) # Add notepad to startup
nirpy.autorun('C:\\Windows', 'notepad.exe', 'you_name', state=False) # Remove notepad from startup

#After executing you can use: 
nirpy.clean() #Clean nirpy cache
nirpy.unload() #Remove nirpy.exe


"""

from setuptools import setup, find_packages

setup(name='nirpy',
      version='1.0.5',
      description='Use nircmdc commands in python',
      long_description='Full description here: https://github.com/LimerBoy/nirpy/blob/master/README.md',
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