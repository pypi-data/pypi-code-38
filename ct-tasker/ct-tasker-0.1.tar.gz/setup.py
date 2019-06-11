from setuptools import setup

def readme():
  with open('README.md') as f:
    return f.read()

setup(name='ct-tasker',
      version='0.1',
      description='Creative Tools interview exercise',
      long_description=readme(),
      keywords='',
      url='http://gitlab.com/OldIronHorse/tasker',
      author='Simon Redding',
      author_email='s1m0n.r3dd1ng@gmail.com',
      license='GPL3',
      packages=['tasker'],
      install_requires=[],
      scripts=['bin/task-run'],
      test_suite='nose.collector',
      tests_require=['nose', 'nosy'],
      include_package_data=True,
      zip_safe=False)
