from setuptools import setup
import os
import sys


def readme():
    with open('README.md') as f:
        return f.read()


# https://github.com/ipython/ipython/blob/master/README.rst#ipython-requires-python-version-3-or-above
if sys.version_info[0] < 3 and 'bdist_wheel' not in sys.argv:
    ipython_dependency = ['ipython<6']
else:
    ipython_dependency = ['ipython']

print('setup.py using python', sys.version_info[0])
print('ipython_dependency:', ipython_dependency)

setup(name='rsp_jupyter',
      version='{major}.{minor}.{patch}'.format(major=os.environ['RSTUDIO_VERSION_MAJOR'], 
                                               minor=os.environ['RSTUDIO_VERSION_MINOR'],
                                               patch=os.environ['RSTUDIO_VERSION_PATCH']),
      description='Jupyter Notebook integration with RStudio Server Pro',
      long_description=readme(),
      long_description_content_type='text/markdown',
      url='https://docs.rstudio.com/ide',
      project_urls={
          "Documentation": "https://docs.rstudio.com/ide",
      },
      author='RStudio',
      author_email='ide@rstudio.com',
      license='GPL-2.0',
      packages=['rsp_jupyter'],
      install_requires=[
          'notebook'
      ] + ipython_dependency,
      include_package_data=True,
      zip_safe=False)
