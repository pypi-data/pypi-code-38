import setuptools
from pathlib import Path
# installed from pypi.org
# -> in terminal: pip install setuptools wheel twine

setuptools.setup(
    name="kbeePDF",
    version=1.0,
    long_description=Path('README.md').read_text(),
    # using .find_packages(keyword_args=[])
    packages=setuptools.find_packages(exclude=['tests', 'data'])
)
