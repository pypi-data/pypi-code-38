from setuptools import setup, find_packages
import os 

PYCLAY_VERSION = os.environ.get('PYCLAY_VERSION', '2.0.dev9')
print("** USING PYCLAY VERSION = %s" % PYCLAY_VERSION)
setup(name='dataClay',
      version=PYCLAY_VERSION,
      install_requires=["enum34;python_version<\"3.4\"",
                        "lru-dict",
                        "Jinja2",
                        "PyYAML<5",
                        "decorator",
                        "grpcio==1.17.1",
                        "grpcio-tools==1.17.1",
                        "protobuf==3.6.1",
                        "psutil",
                        "six"
                        ],
      description='Python library for dataClay',
      packages=find_packages("src"),
      package_dir={'':'src'},
      package_data={
        # All .properties files are valuable "package data"
        '': ['*.properties'],
      },
      )
