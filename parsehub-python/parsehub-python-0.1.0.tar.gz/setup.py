import os

from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='parsehub-python',
      version='0.1.0',
      description='API wrapper for Parsehub written in Python',
      long_description=read('README.md'),
      long_description_content_type="text/markdown",
      url='https://github.com/GearPlug/parsehub-python',
      author='Miguel Ferrer',
      author_email='ingferrermiguel@gmail.com',
      license='MIT',
      packages=['parsehub'],
      install_requires=[
          'requests',
      ],
      zip_safe=False)
