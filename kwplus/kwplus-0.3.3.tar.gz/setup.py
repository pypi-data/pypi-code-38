from setuptools import setup


setup(name='kwplus',
      description='Keyword arguments on steroids',
      author='Vikas Dhiman',
      url='https://github.com/wecacuee/kwplus',
      author_email='dhiman@umich.edu',
      version='0.3.3',
      license='MIT',
      classifiers=(
          'Development Status :: 3 - Alpha',
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ),
      python_requires='>=3.5',
      py_modules=['kwplus', 'kwrepr', 'functoolsplus', 'kwvars'])
