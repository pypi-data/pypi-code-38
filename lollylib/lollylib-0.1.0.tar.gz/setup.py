from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='lollylib',
      version='0.1.0',
      description='A multipurpose Python 3 library that creates an additional abstraction layer \
                    and provides higher level interface for python developers',
      long_description=readme(),
      long_description_content_type="text/markdown",
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords='lollylib',
      url='https://github.com/sugurd/lollylib',
      author='Yuri Zappa',
      author_email='yuzappa@gmail.com',
      license='MIT',
      packages=['lollylib'],
      install_requires=[
          'markdown',
          'semver'
      ],
      include_package_data=True,
      zip_safe=False)
