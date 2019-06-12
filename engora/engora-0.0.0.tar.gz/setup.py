from setuptools import setup

setup(name='engora',
      version='0.0.0',
      description='Python client library for engora.tech',
      url='https://engora.tech',
      author='engora.tech',
      author_email='dsa@engora.tech',
      license='MIT',
      packages=['engora'],
      install_requires=[
          'requests',
          'pint'
      ],
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      zip_safe=False)