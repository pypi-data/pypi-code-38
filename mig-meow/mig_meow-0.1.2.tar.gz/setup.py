from setuptools import setup

with open('README.md', 'r') as readme:
    long_description = readme.read()

setup(name='mig_meow',
      version='0.1.2',
      author='David Marchant',
      author_email='d.marchant@ed-alumni.net',
      description='MiG based manager for event oriented workflows',
      long_description=long_description,
      # long_description_content_type='text/markdown',
      url='https://github.com/PatchOfScotland/mig_meow',
      packages=['mig_meow'],
      classifiers=[
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: OS Independent'
      ])
