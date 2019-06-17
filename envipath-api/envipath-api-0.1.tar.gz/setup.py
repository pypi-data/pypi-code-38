from setuptools import setup

setup(name='envipath-api',
      version='0.1',
      description="wrapper for rest calls to envipath",
      author='Me and others',
      author_email='schmide@ethz.ch',
      license='MIT',
      packages=['envirest'],
      install_requires=['argparse', 'requests'],
      zip_safe=False)
