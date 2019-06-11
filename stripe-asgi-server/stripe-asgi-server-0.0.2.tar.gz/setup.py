import setuptools
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

github_url = "https://github.com/cglacet/stripe-asgi-server"

setuptools.setup(
    name='stripe-asgi-server',
    version='0.0.2',
    description='An asgi server for stripe payments',
    url=github_url,
    project_urls={
        'Bug Reports': f'{github_url}/issues',
        'Source': github_url,
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Christian Glacet',
    author_email='cglacet@kune.tech',
    license='MIT',
    zip_safe=False,
    install_requires=[
        "aiohttp-asynctools >= 0.1.2",
        "fastapi[all] >= 0.29.0",
        "gunicorn",
        "async-stripe >= 0.1.2",
        "Babel >= 2.7.0",
    ],
    setup_requires=[
        "pytest-runner",
    ],
    tests_require=[
        "pytest",
        "pytest-asyncio",
    ],
    packages=setuptools.find_packages(exclude=("tests",)),
    classifiers=(
        "Development Status :: 1 - Planning",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)