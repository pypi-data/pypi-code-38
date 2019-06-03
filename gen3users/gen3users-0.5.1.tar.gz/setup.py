from subprocess import check_output

from setuptools import setup


def get_version():
    try:
        tag = check_output(
            ["git", "describe", "--tags", "--abbrev=0", "--match=[0-9]*"]
        )
        return tag.decode("utf-8").strip("\n")
    except Exception:
        print(
            "The version number cannot be extracted from git tag in this source "
            "distribution; please either download the source from PyPI, or check out "
            "from GitHub and make sure that the git CLI is available."
        )
        raise


def get_readme():
    with open("README.md", "r") as f:
        return f.read()


setup(
    name="gen3users",
    version='0.5.1',
    description="Utils for Gen3 commons user management",
    long_description=get_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/uc-cdis/gen3users",
    license="Apache",
    packages=["gen3users"],
    install_requires=["PyYAML~=5.1", "click", "cdislogging~=1.0.0"],
    entry_points={"console_scripts": ["gen3users=gen3users.main:main"]},
)
