"""
@author: David Diaz Vico
@license: MIT
"""

from setuptools import find_packages, setup


setup(name='scikit-dda',
      packages=find_packages(),
      version='0.1.1',
      description='Scikit-learn-compatible Deep Discriminant Analysis',
      #long_description=open('README.md', 'r').read(),
      author='David Diaz Vico',
      author_email='david.diaz.vico@outlook.com',
      url='https://github.com/daviddiazvico/scikit-dda',
      download_url='https://github.com/daviddiazvico/scikit-dda/archive/v0.1.1.tar.gz',
      keywords=['scikit-learn', 'dda'],
      classifiers=['Intended Audience :: Science/Research',
                   'Topic :: Scientific/Engineering',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.6'],
      install_requires=['scikit-learn'],
      setup_requires=['pytest-runner'],
      tests_require=['coverage', 'pytest', 'pytest-cov'],
      test_suite='tests')
