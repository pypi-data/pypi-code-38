from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='sh_molli',
	  version='0.0.51',
      description='Package to process (sh)MOLLI MRI data',
      long_description=readme(),
      author='Ben George',
      author_email='ben.geroge@oncology.ox.ac.uk',
      packages=['sh_molli'],
      install_requires=[
          'pydicom',
          'numpy',
          'scipy',
          'tqdm',
          'matplotlib'
      ],
      entry_points={
          'console_scripts': ['sh_molli=sh_molli.command_line:main'],
      },
      zip_safe=False)