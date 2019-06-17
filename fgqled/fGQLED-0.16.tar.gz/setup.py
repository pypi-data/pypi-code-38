import setuptools
with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='fGQLED',
    version='0.16',
    author='Killian Keller',
    author_email='kkeller@ethz.ch',
    description='Standard functions used for the QDLED Project at ETH.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['fgqled'],
    classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    ],
)