from setuptools import setup

# TODO: More informative metadata creation

setup(
    name='archtype_user_identification',
    version='0.0.1',
    description='Identify user archtype based on twitter post they make. https://gitlab.lftechnology.com/leapfrogai/archetype-identification',
    author='Sushil Ghimire',
    author_email='sushil79g@gmail.com, sushilghimire@lftechnology.com',
    license='Apache License 2.0',
    packages=['archtype_user_identification'],
    install_requires=[
          'archtype_user_identification'
      ],
    zip_safe=False
)
