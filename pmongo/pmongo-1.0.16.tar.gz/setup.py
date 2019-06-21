from setuptools import setup
import os, io

__version__ = '1.0.16'

here = os.path.abspath(os.path.dirname(__file__))
README = io.open(os.path.join(here, 'README.md'), encoding='UTF-8').read()
CHANGES = io.open(os.path.join(here, 'CHANGES.md'), encoding='UTF-8').read()
setup(name="pmongo",
      version=__version__,
      keywords=('mongo', 'django', 'orm', 'nosql'),
      description="A small Python MongoDB Document-Based access engine.",
      long_description=README + '\n\n\n' + CHANGES,
      long_description_content_type = "text/markdown",
      url='https://github.com/sintrb/pmongo/',
      author="trb",
      author_email="sintrb@gmail.com",
      packages=['pmongo'],
      install_requires=['pymongo', 'six'],
      zip_safe=False
      )
