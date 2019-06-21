from setuptools import setup

tests_require = ['pytest']

setup(name='git-joke-cli',
      version='1.1.1',
      description='Get git joke in command line',
      long_description=open("README.rst").read(),
      long_description_content_type='text/markdown',
      url='https://github.com/vitakrya/git-joke-cli',
      author='Vita Kr',
      license='MIT',
      packages=['gitjoke'],
      scripts=['bin/git-joke'],
      install_requires=['requests', 'docopt', 'halo'],
      setup_requires=['pytest-runner'],
      tests_require=['pytest', 'responses'],
      zip_safe=False)
