from setuptools import setup

tests_require = ['pytest']

setup(name='git-joke-cli',
      version='1.0.0',
      description='Get git joke in command line',
      url='https://github.com/vitakrya/git-joke-cli',
      author='Vita Kr',
      license='MIT',
      packages=['gitjoke'],
      scripts=['bin/git-joke'],
      install_requires=[
          'requests',
          'docopt',
      ],
      setup_requires=['pytest-runner'],
      tests_require=['pytest', 'responses'],
      zip_safe=False)
