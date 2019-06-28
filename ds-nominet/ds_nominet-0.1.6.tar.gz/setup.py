from setuptools import setup

setup(name='ds_nominet',
      version='0.1.6',
      description='',
      url='https://github.com/matthewashby/DS-Nominet',
      author='DS',
      author_email='matt@ashby.co.uk',
      license='NA',
      packages=['ds_nominet'],
      package_data={
            'ds_nominet': ['templates/*'],
      },
      zip_safe=False)
