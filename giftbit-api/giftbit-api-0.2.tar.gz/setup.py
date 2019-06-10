from setuptools import setup

readme_content = ''

with open('README.md', 'r') as f:
  readme_content = f.read()

setup(
  name='giftbit-api',
  version='0.2',
  description='A simplistic API client for Giftbit',
  long_description=readme_content,
  long_description_content_type='text/markdown',
  url='https://github.com/bequest/giftbit-api',
  author='Bequest Inc.',
  author_email='oss@willing.com',
  license='GPLv3',
  packages=['giftbit', 'giftbit.api'],
  zip_safe=False,
)
