from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(name='py_buildsystem',
      version='0.5.0',
      description='python based build system.',
	  long_description=long_description,
	  long_description_content_type='text/markdown',  # This is important!
      url='https://github.com/ProrokWielki/py_buildsystem',
      author='Pawel Warzecha',
      author_email='pawel.warzecha@yahoo.com',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
          'pyyaml',
          'setuptools-git',
          'gitpython'
          ],
      zip_safe=False)