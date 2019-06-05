from setuptools import setup

from mdjpp import __version__ as version

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='mdjpp',
      version='.'.join(map(str,version)),
      description='Journal PreProcessor',
      long_description=readme(),
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Text Processing :: Markup',
      ],
      url='http://github.com/tljm/mdjpp',
      author='Tomasz Magdziarz',
      author_email='tljm@wp.pl',
      test_suite='nose.collector',
      tests_require=['nose'],
      scripts=['apps/mdjpp'],
      license='ISC',
      packages=['mdjpp'],
      zip_safe=False)
