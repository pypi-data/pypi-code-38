"""
General setup for module
"""

from setuptools import setup, find_packages

setup(name='plotje',
      version='1.1',
      python_requires='>3.5',
      install_requires=[
		'matplotlib>=2.2.0', 
        'numpy>=1.16.2'],
      description='Simple matplotlib styling function.',
      packages=find_packages(),
      author='William Hedley Thompson',
      author_email='hedley@startmail.com',
      url='https://www.github.com/wiheto/plotje',
      long_description='Simple matplotlib styling function to make prettier and simplier axes.'
      )
