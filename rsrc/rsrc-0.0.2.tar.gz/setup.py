from pathlib import Path

from setuptools import (find_packages,
                        setup)

import rsrc

project_base_url = 'https://github.com/lycantropos/rsrc/'

install_requires = [
    'reprit>=0.0.1',
    'memoir>=0.0.1',
]
setup_requires = [
    'pytest-runner>=4.2',
]
tests_require = [
    'pytest>=3.8.1',
    'pytest-cov>=2.6.0',
    'hypothesis>=3.73.1',
]

setup(name=rsrc.__name__,
      packages=find_packages(exclude=('tests', 'tests.*')),
      version=rsrc.__version__,
      description=rsrc.__doc__,
      long_description=Path('README.md').read_text(encoding='utf-8'),
      long_description_content_type='text/markdown',
      author='Azat Ibrakov',
      author_email='azatibrakov@gmail.com',
      url=project_base_url,
      download_url=project_base_url + 'archive/master.zip',
      python_requires='>=3.5.3',
      install_requires=install_requires,
      setup_requires=setup_requires,
      tests_require=tests_require)
