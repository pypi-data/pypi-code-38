from setuptools import setup, find_packages


setup(name='kwplus',
      description='Keyword arguments on steroids',
      author='Vikas Dhiman',
      url='https://github.com/wecacuee/kwplus',
      author_email='wecacuee@github.com',
      version='1.0.0',
      license='MIT',
      classifiers=(
          'Development Status :: 3 - Alpha',
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ),
      python_requires='>=3.5',
      packages=find_packages())
