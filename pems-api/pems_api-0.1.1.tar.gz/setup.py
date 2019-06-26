from setuptools import setup

setup(name='pems_api',
      version='0.1.1',
      description='API for PeMS dataset',
      url='https://gitlab.medianets.hu/anagy/pems_api',
      author='Attila Nagy',
      author_email='anagy@hit.bme.hu',
      license='MIT',
      packages=['pems_api'],
      install_requires=[
          'pandas',
          'numpy',
          'tqdm'
      ],
      zip_safe=False)
