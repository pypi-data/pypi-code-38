import setuptools


def readme():
    with open('README.md','r') as f:
        return f.read()

setuptools.setup(
     name='ExperimentManager',  
     version='0.1',
     scripts=['ExperimentManager'] ,
     author="Victor Ruelle",
     author_email="ruelle.victor@gmail.com",
     description="A thoughtless and all-round experiment manager for python",
     long_description=readme(),
     license='MIT',
     install_requires=[
          'numpy',
	  'tensorflow',
	  'keras',
	  'superjson',
	  'wrapt',
	  'matplotlib'
      ],
     long_description_content_type="text/markdown",
     url="https://github.com/victorruelle/ExperimentManager",
     packages=setuptools.find_packages(),
     classifiers=[
         "Development Status :: Programming Language :: Python :: 3",
         "License :: MIT License",
         "Experiment :: Manager",
     ],
     include_package_data=True
 )
