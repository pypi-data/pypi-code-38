from setuptools import setup

with open("LICENSE", "r") as fh:
    license = fh.read()

with open("README.md") as rm:
    long_description = rm.read()

setup(
    name='ppc',
    version='0.0.2',
    install_requires=['requests'],
    python_requires='~=3.7',
    packages=['ppc'],
    url='https://github.com/cloudcraeft/ppc',
    license=license,
    author='cloudcraeft',
    author_email='cloudcraeft@outlook.com',
    description='A Prisma Public Cloud API Client',
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={
        'console_scripts': [
            'ppc = ppc.cli:cli'
        ]
    }
)
