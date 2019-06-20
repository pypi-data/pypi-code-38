from setuptools import setup, find_packages

setup(name='openProductionHW',
      version='0.0.1',
      description='Library to interface HW within openProduction',
      url='https://github.com/Coimbra1984/openProductionHW',
      author='Markus Proeller',
      author_email='markus.proeller@pieye.org',
      license='GPLv3',
      install_requires=[
        "PyDAQmx", "nidaqmx", "pyserial", "crcmod"
      ],
      include_package_data=True,
      packages=find_packages(),
      package_data={'': ['*.py', '*.yapsy-plugin'] },
      zip_safe=False)