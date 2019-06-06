import setuptools

long_description = ''

with open("README.txt", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wrtdk",
    version="1.0.4",
    author="Randall Reynolds",
    author_email="reynolds@whiterivertech.com",
    description="WRT Python 3 Libraries",
    long_description=long_description,
    url="http://www.whiterivertech.com/",
    license='MIT',
    packages=setuptools.find_packages(),
    install_requires=['numpy','matplotlib','scipy','configparser','pyqt5','pyserial','pyvisa','pyvisa-py','pyopengl','scipy','utm'],
    zip_safe=False
)
