from setuptools import setup

def readme_file():
    with open("README.rst") as readme:
        data = readme.read()
    return data

setup(
    name="hs_dl",
    version="1.1.0",
    description="Simple Horrible Subs Downloader",
    long_description=readme_file(),
    author="samyak",
    license="MIT",
    packages=["hs_dl"],
    install_requires=[
        'docopt', 
        'requests',
        'requests-html'
    ],
    project_urls={
        "Documentation": "http://hs-dl.readthedocs.io/",
        "Source Code": "https://github.com/samyakahuja/hs_dl",
    }
)

