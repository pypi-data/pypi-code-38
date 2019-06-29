from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='rocore',
      version='1.0.8',
      description='Core classes and functions, reusable in any kind of Python application',
      long_description=readme(),
      long_description_content_type='text/markdown',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Operating System :: OS Independent'
      ],
      url='https://github.com/RobertoPrevato/rocore',
      author='RobertoPrevato',
      author_email='roberto.prevato@gmail.com',
      keywords='core utilities',
      license='MIT',
      packages=['rocore',
                'rocore.typesutils',
                'rocore.decorators'],
      install_requires=[],
      include_package_data=True,
      zip_safe=False)
