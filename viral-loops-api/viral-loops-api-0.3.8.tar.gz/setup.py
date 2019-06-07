from setuptools import setup

readme_content = ''

with open('README.md', 'r') as f:
  readme_content = f.read()

setup(
  name='viral-loops-api',
  version='0.3.8',
  description='A simplistic API wrapper for viral-loops',
  long_description=readme_content,
  long_description_content_type='text/markdown',
  url='https://github.com/bequest/viral-loops-api',
  author='Bequest Inc.',
  author_email='oss@willing.com',
  license='GPLv3',
  packages=['viral_loops_api'],
  zip_safe=False,
)
