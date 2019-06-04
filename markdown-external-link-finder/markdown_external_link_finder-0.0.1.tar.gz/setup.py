from setuptools import setup

setup(name='markdown_external_link_finder',
      version='0.0.1',
      description='Finds external links in markdown files',
      url='http://github.com/matmoore/markdown-external-link-finder',
      license='MIT',
      packages=['markdown_external_link_finder'],
      author='Mat Moore',
      author_email='MatMoore@users.noreply.github.com',
      python_requires='>=3.6',
      install_requires='mistune')