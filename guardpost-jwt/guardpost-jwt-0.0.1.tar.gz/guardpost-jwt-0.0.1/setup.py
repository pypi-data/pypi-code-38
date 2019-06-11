from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='guardpost-jwt',
      version='0.0.1',
      description='Classes to use JWT Bearer authentication with GuardPost.',
      long_description=readme(),
      long_description_content_type='text/markdown',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Operating System :: OS Independent'
      ],
      url='https://github.com/RobertoPrevato/GuardPost-JWT',
      author='RobertoPrevato',
      author_email='roberto.prevato@gmail.com',
      keywords='authentication authorization jwt oauth',
      license='MIT',
      packages=['guardpost-jwt'],
      install_requires=['guardpost',
                        'pyjwt'],
      include_package_data=True,
      zip_safe=False)
