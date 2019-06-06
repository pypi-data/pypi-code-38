from setuptools import setup

setup(name='dredging',
      version_format='{tag}.dev{commitcount}+{gitsha}',
      setup_requires=['setuptools-git-version'],
      description='Collection of helper functions for dredging math',
      long_description='Collection of helper functions for dredging math',
      url='https://github.com/Flawless/dredging',
      author='Alexander Ushanov',
      author_email='alushanov92@gmail.com',
      license='MIT',
      packages=['dredging'],
      zip_safe=False)
