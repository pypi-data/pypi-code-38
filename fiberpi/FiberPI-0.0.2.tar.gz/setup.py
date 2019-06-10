import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="FiberPI",
    version="0.0.2",
    author="Christopher Mendoza",
    author_email="camendoza7@miners.utep.edu",
    description="Package to detect contaminated fiber connectors",
    long_description='''
# FiberPI
Package that automates detecting contaminated fiber connectors between switches using the switch CLIs.
[Github Link](https://github.com/utepnetlab/fiberPI)

## Installation

```bash
pip install FiberPI
```

## Usage
```python
import FiberPI as FPI

#Create the two switches
ubnt = FPI.node('Ubiquiti', '192.168.1.1', 'ubiquiti_edgeswitch', 'user', 'pass')
dlink = FPI.node('D-Link', '192.168.1.2', 'dlink_dgs', 'user', 'pass')

#Create the connection using a context manager to open and close connections
with FPI.connection('conn', ubnt, dlink, 1, 27, 0, 1, 1) as conn:
    #Detect Contamination
    result = conn.DetectContamination()
```
## Contributing
Anyone is welcome to contribute, if you'd like send a pull request for major changes with the changes you'd like to make.

## License
[MIT](https://choosealicense.com/licenses/mit/)
''',
    long_description_content_type="text/markdown",
    url="https://github.com/utepnetlab/fiberPI",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)