from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
]

setup(
    name            = 'evidencer',
    packages        = find_packages(),
    package_data    = {'extractors': ['*.py', '*.yapsy-plugin'],
                       'extractors_pre_configurations': ['*.json'],
                       'test_logs': ["*.txt"]},
    version         = '0.1',
    description     = '',
    author          = 'Jan Seda',
    author_email    = 'xsedaj00@gmail.com',
    url             = 'https://github.com/Honzin/evidencer',
    download_url    = '',
    install_requires=[],
    keywords        = ["testing", "logs", "extraction"],
    classifiers     = classifiers,
)

