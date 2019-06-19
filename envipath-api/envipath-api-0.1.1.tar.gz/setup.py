from setuptools import setup

setup(name='envipath-api',
      version='0.1.1',
      description="wrapper for rest calls to envipath",
      author='Emanuel Schmid',
      author_email='schmide@ethz.ch',
      license='MIT',
      url='https://github.com/emanuel-schmid/envipath-api',
      packages=['envirest'],
      install_requires=['argparse', 'requests'],
      zip_safe=False)
