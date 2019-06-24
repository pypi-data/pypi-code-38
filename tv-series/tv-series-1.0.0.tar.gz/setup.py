import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tv-series",
    version="1.0.0",
    author="Ali Kaafarani",
    author_email="ali@kvikshaug.no",
    url="https://gitlab.com/kvikshaug/tv",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    py_modules=["tv"],
    install_requires=["click", "requests", "tabulate", "xdg"],
    extras_require={"dev": ["black", "flake8", "flake8-bugbear", "isort"]},
    entry_points="""
        [console_scripts]
        tv=tv.tv:cli
    """,
)
