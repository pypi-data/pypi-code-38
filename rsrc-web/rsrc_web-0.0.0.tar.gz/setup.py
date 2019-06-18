from pathlib import Path

from setuptools import (find_packages,
                        setup)

import rsrc_web

project_base_url = 'https://github.com/lycantropos/rsrc_web/'

setup_requires = [
    'pytest-runner>=4.2',
]
tests_require = [
    'pytest>=3.8.1',
    'pytest-cov>=2.6.0',
    'hypothesis>=3.73.1',
]

setup(name=rsrc_web.__name__,
      packages=find_packages(exclude=('tests', 'tests.*')),
      version=rsrc_web.__version__,
      description=rsrc_web.__doc__,
      long_description=Path('README.md').read_text(encoding='utf-8'),
      long_description_content_type='text/markdown',
      author='Azat Ibrakov',
      author_email='azatibrakov@gmail.com',
      url=project_base_url,
      download_url=project_base_url + 'archive/master.zip',
      python_requires='>=3.5',
      setup_requires=setup_requires,
      tests_require=tests_require)
