from setuptools import setup
import codecs

setup(
    name='nudb',
    version = '1.1.4',
    description = 'For nudb',
    long_description = codecs.open('README.md', 'r', 'utf-8').read(),
    long_description_content_type = 'text/markdown',
    author = 'Szu-Hsuan, Wu',
    author_email = 'shuan@csie.io',
    url = 'https://github.com/wshs0713/nudb',
    packages = ['nudb'],
    keywords = ['nudb'],
    license = 'docs/LICENSE.txt',
    install_requires=[
        'requests >= 2.18.0'
    ]
)
