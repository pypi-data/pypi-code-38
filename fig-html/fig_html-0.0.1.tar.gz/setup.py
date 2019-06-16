from setuptools import setup, find_packages
from os import path

project_root = path.abspath(path.dirname(__file__))
with open(path.join(project_root, 'README.md'), encoding='utf-8') as f:
    readme = f.read()

setup(
    name='fig_html',
    version='0.0.1',
    description='html generator following directory structure you saved figures',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Kazeto Fukasawa',
    author_email='fukasawakaze@gmail.com',
    url='https://github.com/kazetof/fig_html',
    license='MIT',
    install_requires=['numpy', 'pandas', 'jinja2>=2.10', "matplotlib"],
    packages=find_packages(exclude=('tests')),
    test_suite='tests',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords="python data-science data-analysis"
)