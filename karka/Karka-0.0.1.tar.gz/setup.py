from setuptools import setup

from os import path

here = path.abspath(path.dirname(__file__))

setup(
  name='Karka',
  packages=['karka'],
  version='0.0.1',
  description='A TensorFlow recommendation algorithm and framework in Python.',
  author='Aaron Ma',
  author_email='hi@aaronhma.com',
  url='https://github.com/firebolt-ai/karka/',
  license='MIT',
  keywords=['python', 'python3', 'tensorflow', 'recommendation', 'pypi', 'karka', 'firebolt', 'ai', 'algorithm', 'framework'],
  classifiers=[],
  install_requires=[
      "numpy>=1.14.1",
      "scipy>=0.19.1",
      "six==1.11.0",
      "tensorflow>=1.7.0",
  ],
)
