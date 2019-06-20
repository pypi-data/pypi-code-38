__author__ = 'schien'

from setuptools import setup

# def read(*paths):
#     """Build a file path from *paths* and return the contents."""
#     with open(os.path.join(*paths), 'r') as f:
#         return f.read()
#

# long_description = pypandoc.convert('README.md', 'rst')
# with open('excel_helper/version.py') as f: exec(f.read())
setup(
    setup_requires=['pbr'],
    pbr=True,
)