from setuptools import setup


with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()


setup(
    name='cows',
    version='1.0.1',
    author='Aaron M. Rosenfeld',
    author_email='aaron@rosenfeld.io',
    url='https://github.com/arosenfeld/cows',
    packages=[
        'cows',
    ],

    description='''Simple, efficient collections for strings with
    wildcards.''',
    long_description=long_description,
    long_description_content_type='text/markdown',
)
