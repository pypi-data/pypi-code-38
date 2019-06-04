import setuptools

setuptools.setup(
    name='objcrypt',
    version='0.2',
    scripts=['objcrypt'],
    author='Max Bridgland',
    author_email='mabridgland@protonmail.com',
    description='Easily Encrypt and Decrypt Python and JSON Objects',
    long_description='Easily Encrypt and Decrypt Python and JSON Objects',
    url='https://github.com/M4cs/objcrypt',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent"
    ]
)
