from setuptools import setup

setup(name='azure_keyvault_ethereum_py',
      version='0.2',
      description='Ethereum Keyvault',
      url='https://github.com/davidp94/azure-keyvault-ethereum-py',
      author='David Phan',
      license='MIT',
      packages=['azure_keyvault_ethereum_py'],
      install_requires=[
          "eth-keys==0.2.2",
          "secp256k1==0.13.2",
          "azure-keyvault==1.1.0",
          "eth-account==0.4.0"
      ],
      zip_safe=False)
