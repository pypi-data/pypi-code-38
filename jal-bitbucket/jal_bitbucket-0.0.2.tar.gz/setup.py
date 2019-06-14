from setuptools import setup

setup(name='jal_bitbucket',
      version='0.0.2',
      description='Retrieve info from BitBucket API',
      url='http://github.com/jalgraves/bitbucket',
      author='Jonny Graves',
      author_email='jalgraves@yahoo.com',
      license='MIT',
      packages=['jal_bitbucket'],
      zip_safe=False,
      install_requires=['requests'],
      include_package_data=True
      )
