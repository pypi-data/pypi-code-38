from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()

classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
]

setup(
    name            = 'evidencer',
    packages        = find_packages(),
    package_data    = {'extractors': ['*.*'],
                       'extractors_pre_configurations': ['*.*']},
    version         = '0.2',
    description     = 'Framework for modular extraction information.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    author          = 'Jan Seda',
    author_email    = 'xsedaj00@gmail.com',
    url             = 'https://github.com/Honzin/evidencer',
    download_url    = '',
    install_requires=["jsonmerge", "yapsy"],
    keywords        = ["testing", "logs", "extraction"],
    classifiers     = classifiers,
)

