from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()


setup(name='ping_cmd',
      version='1.5',
      description='Ping website or server using ping.exe just to check is the host reachable or not.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Dragan Matesic',
      author_email='dragan.matesic@gmail.com',
      license='MIT',
      packages=['ping_cmd'],
      zip_safe=False
      )
