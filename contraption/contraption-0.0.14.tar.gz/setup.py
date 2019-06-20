import setuptools

setuptools.setup(
    name="contraption",
    version="0.0.14",
    author="William Wyatt",
    author_email="wwyatt@ucsc.edu",
    description="pyvisa support for powersupplies DPO and DAQs (Aglient, Keithley, Tektronix, Lecroy)",
    long_description="pyvisa support for powersupplies DPO and DAQs (Aglient, Keithley, Tektronix, Lecroy)",
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    url="https://github.com/Tsangares/Devices",
    #scripts=['probecard/bin/probecard'],
    install_requires=[
        "PyVISA==1.9.1",
        "numpy==1.16.2",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
