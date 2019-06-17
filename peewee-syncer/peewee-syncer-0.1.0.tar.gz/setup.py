from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(name='peewee-syncer',
      description='Tiny Sync tool using Peewee Models for persistance',
      long_description=long_description,
      long_description_content_type="text/markdown",
      version='0.1.0',
      url='https://github.com/hampsterx/peewee-syncer',
      author='Tim van der Hulst',
      author_email='tim.vdh@gmail.com',
      license='Apache2',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3'
      ],
      packages=['peewee_syncer'],
      install_requires=[
            'peewee>=3.8.1',
            'python-dateutil>=2.7.5',
      ],
    extras_require={
        "async": ["peewee-async==0.6.0a0"],
        "async-pg": ["peewee-asyn==0.6.0a0", "aiopg>=0.16.0"],
        "async-mysql": ["peewee-asyn==0.6.0a0", "aiomysql>=0.0.20"],

    }
)

