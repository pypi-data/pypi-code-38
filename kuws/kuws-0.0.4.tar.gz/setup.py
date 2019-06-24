"""
Description:
    Contains all the configuration for the package on\
        pypi/pip
"""
import setuptools

def read(*filenames, **kwargs):
    import io
    # Code originally from https://github.com/aegirhall/console-menu/blob/develop/setup.py
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

# Appending the changelog to the readme for a complete package description
long_description = read("README.md", "CHANGELOG.md")

setuptools.setup(
    name="kuws",
    version="0.0.4",
    author="Kieran Wood",
    author_email="kieranw098@gmail.com",
    description="A set of python scripts for common web tasks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Descent098/kuws",
    packages=setuptools.find_packages(),
    entry_points={
          'console_scripts': ['kuws = kuws.command_line_utility:main']
      },
    install_requires=[
    "requests"
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)