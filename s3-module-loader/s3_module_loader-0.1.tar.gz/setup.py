from setuptools import setup

setup(name='s3_module_loader',
      version='0.1',
      description='A module loader to load python packages from s3 buckets',
      url='https://github.com/ablerman/S3ModuleLoader',
      author='Sandy Lerman',
      author_email='alex@ablerman.com',
      license='MIT',
      packages=['s3_module_loader'],
      zip_safe=False)
