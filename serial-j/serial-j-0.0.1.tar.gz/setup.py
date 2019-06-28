import setuptools

setuptools.setup(
    name='serial-j',
    version='0.0.1',
    author='Junpu Fan',
    author_email='junpufan@me.com ',
    description=('making python class out of python dictionary, with '
                 'default conversion method to json string or back to '
                 'python dictionary.'),
    url='https://github.com/JunpuFan/serial-j',
    license='MIT',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
