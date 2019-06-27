import os
import sys

import setuptools


def scm_config():
    here = os.path.dirname(os.path.abspath(__file__))
    egg_info = os.path.join(here, "setuptools_scm_semver.egg-info")
    has_entrypoints = os.path.isdir(egg_info)
    import pkg_resources

    sys.path.insert(0, here)
    pkg_resources.working_set.add_entry(here)
    from setuptools_scm.hacks import parse_pkginfo
    from setuptools_scm_semver.git import parse as parse_git
    from setuptools_scm_semver.version import guess_next_semver_version, get_local_empty

    def parse(root):
        try:
            return parse_pkginfo(root)
        except IOError:
            return parse_git(root)

    config = dict(
        version_scheme=guess_next_semver_version, local_scheme=get_local_empty
    )

    if has_entrypoints:
        return dict(use_scm_version=config)
    else:
        from setuptools_scm import get_version

        return dict(version=get_version(root=here, parse=parse, **config))


with open("README.md") as fp:
    long_description = fp.read()

meta = dict(
    name="setuptools-scm-semver",
    url="https://github.com/hbasria/setuptools-scm-semver",
    version="0.1.3",
    zip_safe=True,
    author="Basri",
    author_email="h@basri.me",
    description="the blessed package to manage your versions by scm tags",
    long_description=long_description,
    license="MIT",
    packages=["setuptools_scm_semver"],
    setup_requires=["setuptools-scm"],
    entry_points="""
        [setuptools_scm.parse_scm]
        .git = setuptools_scm_semver.git:parse

        [setuptools_scm.version_scheme]
        guess-next-semver = setuptools_scm_semver.version:guess_next_semver_version

        [setuptools_scm.local_scheme]
        get-local-empty = setuptools_scm_semver.version:get_local_empty
    """,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Version Control",
        "Topic :: System :: Software Distribution",
        "Topic :: Utilities",
    ],
)

if __name__ == "__main__":
    setuptools.setup(**meta)
