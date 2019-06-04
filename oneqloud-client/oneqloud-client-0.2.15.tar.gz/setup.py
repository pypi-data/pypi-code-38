from setuptools import setup

setup(name='oneqloud-client',
      version='0.2.15',
      description='Client Library for 1QBit Quantum Cloud',
      url='http://1qbit.com',
      author='1QB Information Technologies',
      author_email='info@1qbit.com',
      license='APLv2',
      packages=['oneqloud_client'],
      package_data={
        'oneqloud_client': ['ca.pem'],
      },
      install_requires=[
          'requests',
          'grpcio-tools',
          'future',
          'googleapis-common-protos'
      ],
      zip_safe=False)
