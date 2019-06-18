import setuptools

with open('README.md','r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='DemoModule_pkg',
    version = '0.1.0',
    authour = 'mart',
    author_email = '2012918121@qq.com',
    descripthion = 'An example for teaching how to publishi a Python package',
    long_description = long_description,
    url = 'https://github.com/pypa/sampleproject',
    packages = setuptools.find_packages(),
    classifiers = [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)