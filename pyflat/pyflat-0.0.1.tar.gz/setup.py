import setuptools

with open("README.md") as f:
    long_description = f.read()

setuptools.setup(
    name='pyflat',
    url='https://github.com/noverde/pyflat',
    author='Rafael Izidoro',
    author_email='izidoro.rafa@gmail.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    version='0.0.1',
    description='Python library to transform objects into positional flat string lines',
    packages=setuptools.find_packages(),
    license="MIT",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Customer Service',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ]
)