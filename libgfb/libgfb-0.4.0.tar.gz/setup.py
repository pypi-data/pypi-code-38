import setuptools

setuptools.setup(
    name='libgfb',
    version='0.4.0',
    author='Antony B Holmes',
    author_email='antony.b.holmes@gmail.com',
    description='A library for reading and writing binary gene database files.',
    url='https://github.com/antonybholmes/libgfb',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
)
