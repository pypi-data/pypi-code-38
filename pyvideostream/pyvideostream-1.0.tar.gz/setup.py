import setuptools

with open('README.md', 'r') as readme:
  long_description = readme.read()

setuptools.setup(
      name='pyvideostream',
      version='1.0',
      description='Package that enables video streaming over the same machine',
      url='https://github.com/victorcmoura/python-video-stream',
      author='Victor Moura',
      author_email='victor_cmoura@hotmail.com',
      license='GPL-3.0',
      packages=setuptools.find_packages(),
      zip_safe=False,
      long_description_content_type="text/markdown",
      long_description=long_description,
      install_requires=['pygame']
)