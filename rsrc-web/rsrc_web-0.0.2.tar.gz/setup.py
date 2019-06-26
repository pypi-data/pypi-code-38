from pathlib import Path

from rsrc import plugins
from setuptools import (find_packages,
                        setup)

import rsrc_web
from rsrc_web import base

plugins_entry_points = [
    plugins.to_entry_point(id_=plugins.to_id('http'),
                           module_name=base.__name__,
                           function_name=base.deserialize.__qualname__),
    plugins.to_entry_point(id_=plugins.to_id('https'),
                           module_name=base.__name__,
                           function_name=base.deserialize.__qualname__),
]
project_base_url = 'https://github.com/lycantropos/rsrc_web/'

install_requires = Path('requirements.txt').read_text()
setup_requires = [
    'pytest-runner>=4.2',
]
tests_require = Path('requirements-tests.txt').read_text()

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
      python_requires='>=3.5.3',
      entry_points={plugins.__name__: plugins_entry_points},
      install_requires=install_requires,
      setup_requires=setup_requires,
      tests_require=tests_require)
