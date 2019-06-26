import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()


setuptools.setup(
    name = 'nameko_wrapper',
    version = '0.0.6',
    author = 'li1234yun',
    author_email = 'li1234yun@163.com',
    description = 'nameko wrapper',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/li1234yun/nameko-wrapper',
    packages = setuptools.find_packages(),
    install_requires = [
        'nameko',
        'marshmallow>2',
        'elasticsearch_dsl>=6,<7'
    ],
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
