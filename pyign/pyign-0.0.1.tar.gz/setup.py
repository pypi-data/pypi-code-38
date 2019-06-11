from setuptools import setup, find_packages


setup(
    name = 'pyign',
    version = '0.0.1',
    author = 'Devon Burson',
    author_email = 'devon.burson@gmail.com',
    description = 'A Liquid Rocket Engine python controls package',
    #long_description = long_description,
    #long_description_content_type = 'text/markdown',
    url = 'https://github.com/devonburson/PyIGN',
    packages = find_packages(),
    classifiers = [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
    ],
)
