from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='filelog',
      version='1.0.2',
      description='json supported easy debugger for python, in files. can also read.',
      long_description=readme(),
      long_description_content_type='text/markdown',
      classifiers=[
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Text Processing :: Linguistic',
         'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords='json supported easy debugger for python debug file writer reader',
      url='https://github.com/ebsaral/filelog',
      author='Emin Bugra Saral',
      author_email='eminbugrasaral@me.com',
      license='BSD',
      packages=['filelog'],
      install_requires=[],
      include_package_data=True,
      zip_safe=False,
      project_urls={
        'Documentation': 'https://github.com/ebsaral/filelog',
        'Funding': 'https://github.com/ebsaral/filelog',
        'Source': 'https://github.com/ebsaral/filelog',
      },
)
