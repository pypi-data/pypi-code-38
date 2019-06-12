import io
import os
from setuptools import setup


# pip workaround
os.chdir(os.path.abspath(os.path.dirname(__file__)))


# Need to specify encoding for PY3, which has the worst unicode handling ever
with io.open('README.md', encoding='utf-8') as fp:
    description = fp.read()
setup(name='unix_ar',
      version='0.2.1',
      py_modules=['unix_ar'],
      python_requires='~=3.6',
      description="AR file handling",
      author="Remi Rampin",
      author_email='remirampin@gmail.com',
      maintainer="Alan Justino",
      maintainer_email='alan.justino@yahoo.com.br',
      url='https://github.com/getninjas/unix_ar',
      long_description=description,
      long_description_content_type='text/markdown',
      license='BSD',
      keywords=['ar', 'archive', 'unix', 'deb'],
      classifiers=[  # yapf: nolint
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3',
          'Operating System :: OS Independent',
          'Topic :: System :: Archiving',
          'Topic :: Utilities'])
