from setuptools import setup

setup(name='jcat',
      version='1',
      description='display json in flat format',
      url='https://git.osuv.de/m/jcat',
      author='Markus Bergholz',
      author_email='markuman@gmail.com  ',
      license='WTFPL',
      packages=['jcat'],
      scripts=['bin/jcat'],
      zip_safe=True)
