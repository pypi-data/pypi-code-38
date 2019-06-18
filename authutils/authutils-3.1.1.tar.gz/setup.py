from subprocess import check_output

from setuptools import setup, find_packages


def get_version():
    # https://github.com/uc-cdis/dictionaryutils/pull/37#discussion_r257898408
    try:
        tag = check_output(
            ["git", "describe", "--tags", "--abbrev=0", "--match=[0-9]*"]
        )
        return tag.decode("utf-8").strip("\n")
    except Exception:
        raise RuntimeError(
            "The version number cannot be extracted from git tag in this source "
            "distribution; please either download the source from PyPI, or check out "
            "from GitHub and make sure that the git CLI is available."
        )


setup(
    name="authutils",
    version='3.1.1',
    description="Gen3 auth utility functions",
    license="Apache",
    packages=find_packages(),
    install_requires=[
        "addict~=2.1",
        "Authlib~=0.11",
        "Flask>=0.10.1",
        "requests~=2.6",
        "python-keystoneclient~=1.8",
        "PyJWT~=1.5",
        "Werkzeug~=0.12",
        "xmltodict~=0.9",
        "cached-property~=1.4",
        "cdislogging",
        "cdiserrors~=0.1",
    ],
)
