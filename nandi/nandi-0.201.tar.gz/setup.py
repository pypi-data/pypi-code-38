from setuptools import setup

# Use this site for building the package
# https://uoftcoders.github.io/studyGroup/lessons/python/packages/lesson/

setup(name='nandi',
      version='0.201',
      description='Simple data get utilities to pull stock data from web',
      url='http://github.com/nandi-git/nandi-package',
      author='Satish Nandi',
      author_email='satish@nandi.net',
      license='MIT',
      packages=['nandi'],
      install_requires=[
          'numpy','pandas',
          'requests_html',
          'yahoo_fin'
      ],
      zip_safe=False)
