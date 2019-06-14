import setuptools

with open('VERSION') as f:
    __version__ = f.read().strip()
    assert __version__

def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    with open(filename, 'r') as f:
        lineiter = list(line.strip() for line in f)
    return [line for line in lineiter if line and not line.startswith("#")]

install_reqs = parse_requirements("requirements.txt")

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="soneti",
    version=__version__,
    author="Grupo de Sistemas Inteligentes",
    author_email="lab-gsi@dit.upm.es",
    description="Luigi Tasks for Soneti Orchestration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://lab.gsi.upm.es/social/soneti",
    install_requires=install_reqs,
    packages=['soneti'],
    classifiers=[],
    include_package_data=True
)
