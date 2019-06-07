from distutils.core import setup

with open('README') as file:
    readme = file.read()

setup(
    name='magicWorld',
    version='2.0.0',
    packages=['wargame'],
    url='https://testpypi.python.org/pypi/magicworld/',
    license='LICENSE.txt',
    description='my fantasy game',
    long_description=readme,
    author='jinxingw',
    aythor_email='your_email'
)