import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pysmoothstreams',
    version='0.6',
    url='https://github.com/aaearon/pysmoothstreams',
    license='MIT',
    author='Tim Schindler',
    author_email='',
    description='A Python library for SmoothStreams',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3 :: Only'
    ]
)