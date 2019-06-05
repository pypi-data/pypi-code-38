from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='backutil',
      version='0.1.5',
      description='Python backup utility',
      long_description=readme(),
      long_description_content_type="text/markdown",
      url='https://github.com/heywoodlh/backutil',
      author='Spencer Heywood',
      author_email='l.spencer.heywood@gmail.com',
      license='APACHE-2.0',
      packages=['backutil'],
      scripts=['bin/backutil'],
      install_requires=[
          'requests',
          'python-gnupg',
      ],
      zip_safe=False)
