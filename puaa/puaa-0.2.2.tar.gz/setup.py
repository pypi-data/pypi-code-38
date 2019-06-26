from setuptools import setup

setup(
    name = 'puaa',
    version = '0.2.2',
    description = 'Python UAA test server',
    url = 'https://gitlab.com/romk/puaa',
    license = 'MIT',
    author = 'romk',
    author_email = 'r0mk@gmx.net',
    install_requires = [
        'Authlib',
        'Flask',
        'gunicorn[gevent]',
        'PyYAML>=3.12',
    ],
    packages = ['puaa'],
    python_requires = '>=3',
    long_description = open('README.md').read(),
    long_description_content_type = 'text/markdown',
    include_package_data = True,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing :: Mocking',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ]
)
