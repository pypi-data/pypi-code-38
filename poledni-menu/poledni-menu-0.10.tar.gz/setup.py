from poledni_menu import version
from setuptools import setup
from pathlib import Path

readme = Path(__file__).with_name("README.rst").read_text()


setup(
    name="poledni-menu",
    version=version.VERSION,
    description="Scrap daily menu and send it via e-mail",
    long_description=readme,
    long_description_content_type="text/x-rst",
    url=version.URL,
    author="Ondřej Caletka",
    author_email="ondrej@caletka.cz",
    license="MIT",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Utilities",
    ],
    packages=["poledni_menu", "poledni_menu.extractors"],
    install_requires=[
        "click",
        "lxml",
        "pyyaml",
        "markdown",
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest-vcr"],
    entry_points={
        "console_scripts": [
            "poledni-menu-print = poledni_menu.generate:print_menu",
            "poledni-menu-digest = poledni_menu.digest:print_digest",
            "poledni-menu-email = poledni_menu.email_menu:email_digest",
        ],
    },
)
