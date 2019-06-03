from setuptools import setup

with open('README.md') as readme:
  long_description = readme.read()

setup(
    name='girder-monkeybrains',
    version='1.0.2',
    description='Displays monkey neurodevelopmental data.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/girder/monkeybrains',
    maintainer='Kitware, Inc.',
    maintainer_email='kitware@kitware.com',
    packages=['girder_monkeybrains'],
    install_requires=['girder'],
    include_package_data=True,
    entry_points={
      'girder.plugin': [
          'monkeybrains = girder_monkeybrains:MonkeybrainsPlugin'
      ]
    }
)
