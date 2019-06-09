import ast
import io
import re

from setuptools import setup, find_packages

with io.open('README.md', 'rt', encoding="utf8") as f:
    readme = f.read()

_description_re = re.compile(r'description\s+=\s+(?P<description>.*)')

with open('lektor_netlify_lfs_resize_url.py', 'rb') as f:
    description = str(ast.literal_eval(_description_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    author='Jonathan Mason',
    author_email='jm0804@protonmail.ch',
    description=description,
    keywords='Lektor plugin',
    license='MIT',
    long_description=readme,
    long_description_content_type='text/markdown',
    name='lektor-netlify-lfs-resize-url',
    packages=find_packages(),
    py_modules=['lektor_netlify_lfs_resize_url'],
    # url='[link to your repository]',
    version='0.1.1',
    classifiers=[
        'Framework :: Lektor',
        'Environment :: Plugins',
    ],
    entry_points={
        'lektor.plugins': [
            'netlify-lfs-resize-url = lektor_netlify_lfs_resize_url:NetlifyLfsResizeUrlPlugin',
        ]
    }
)
