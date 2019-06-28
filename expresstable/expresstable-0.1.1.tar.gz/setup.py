import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='expresstable',
    version='0.1.1',
    author='Christopher Smith',
    description='Quickly create tables in Python',
    url='https://github.com/christopherdavidsmith/expresstable',
    packages=setuptools.find_packages(),
    install_requires=[
        'termcolor>=1.1.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)
