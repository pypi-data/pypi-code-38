
# -----------------------------------------------------------------------------
# This source file has been developed within the scope of the
# Technical Director course at Filmakademie Baden-Wuerttemberg.
# http://technicaldirector.de
#
# Written by Tim Lehr
# Copyright (c) 2019 Animationsinstitut of Filmakademie Baden-Wuerttemberg
# -----------------------------------------------------------------------------

import platform
import os
import sys
import pkg_resources
import requests

from abc import abstractmethod
from bs4 import BeautifulSoup


def _get_config_dict():
    config = {"platform": ["any"], "python": []}
    system = platform.system()

    # SYSTEM
    if "Linux" in system:
        config["platform"] += ["lnx", "linux"]
    elif "Mac" in system:
        config["platform"] += ["mac", "macosx", "darwin"]
    elif "Windows" in system:
        config["platform"] += ["win", "windows"]

    # PYTHON
    if sys.version_info > (3, 0):
        config["python"] += ["py3", "36"]
    else:
        config["python"] += ["py2", "26", "27"]
    return config


config_dict = _get_config_dict()


def get_installed_version_str(self, package):
    dist = pkg_resources.get_distribution(package)
    return dist.version


class PackageIndex(object):
    def __init__(self, index_base_url):
        self._url = index_base_url[:-1] if index_base_url.endswith('/') else index_base_url
        self._index_cache = None

    def __repr__(self):
        return "<PackageIndex, '{}'>".format(self.base_url)

    @property
    def base_url(self):
        return self._url

    @property
    def index_url(self):
        return "{}/simple".format(self._url)

    @property
    def online(self):
        try:
            r = requests.get(self._url)
            r.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xxx
            return True
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return False
        except requests.exceptions.HTTPError:
            return False

    def _get_soup(self, package):
        response = requests.get("{server}/{pkg}".format(server=self.index_url,
                                                        pkg=(package or "")))
        if response.status_code == 200:
            return BeautifulSoup(response.content, 'html.parser')
        if response.status_code == 404:
            raise PackageNotAvailableException
        raise HttpRequestException

    def _get_metadata(self, package):
        soup = self._get_soup(package.lower())
        return [PackageMetadata.create(self, package, a.get_text(), a.get('href')) for a in soup.find_all('a')]

    def _filter_packages(self, pkgs):
        filtered = []
        for pkg in pkgs:
            for plat in config_dict["platform"]:
                if plat not in pkg.platform:
                    continue

            for py in config_dict["python"]:
                if py in pkg.python:
                    continue

            filtered.append(pkg)
        return filtered

    def _get_available_packages(self, cached):
        if not self._index_cache or not cached:
            soup = self._get_soup(None)
            pkg_names = [a.get_text() for a in soup.find_all('a')]
            self._index_cache = pkg_names
        return self._index_cache

    def provides_package(self, package):
        return package.lower() in [x.lower() for x in self.get_all_packages_str()]

    def get_all_packages_str(self, cached=True):
        return self._get_available_packages(True)

    def get_newest_version(self, package, filter=True):
        pkgs = self._get_metadata(package)
        if filter:
            pkgs = self._filter_packages(pkgs)
        return pkgs[0] if pkgs else None

    def get_all_versions(self, package, filter=False):
        if filter:
            return self._filter_packages(self._get_metadata(package))
        return self._get_metadata(package)


class PackageMetadata(object):
    @abstractmethod
    def __init__(self, server, url, distribution, version, build, python, abi, platform):
        self._pkg_type = None
        self._server = server
        self._url = url
        self._distribution = distribution
        self._version = version
        self._build = build
        self._python = python
        self._abi = abi
        self._platform = platform

    def __repr__(self):
        return "<'{dist}' ({typ}, v{ver}, '{serv}')>".format(dist=self.distribution,
                                                            typ=self.pkg_type,
                                                            ver=self.version,
                                                            serv=self.server)

    @property
    def pkg_type(self):
        return self._pkg_type

    @property
    def server(self):
        return self._server

    @property
    def url(self):
        return "{}{}".format(self.server.base_url, self._url)

    @property
    def distribution(self):
        return self._distribution

    @property
    def version(self):
        return self._version

    @property
    def build(self):
        return self._build

    @property
    def python(self):
        return self._python

    @property
    def abi(self):
        return self._abi

    @property
    def platform(self):
        return self._platform

    @classmethod
    def create(cls, server, package, filename, url):
        com = filename.split("-")

        # remove extension from last component
        ext = com[-1].partition(".")[0]
        com[-1] = ext

        if filename.endswith('.whl'):
            if len(com) < 6:
                com.insert(2, None)  # insert None for optional build tag (that is missing)
            return WheelMetadata(server, url, *com)
        elif filename.endswith('.tar.gz'):
            # TODO: TARBALL SUPPORT
            raise UnknownPackageTypeException
        else:
            raise UnknownPackageTypeException

    def as_dict(self):
        attrs = ["url",
                 "distribution",
                 "version",
                 "build",
                 "python",
                 "abi",
                 "platform"]
        return {attr: getattr(self, attr) for attr in attrs}


class WheelMetadata(PackageMetadata):
    def __init__(self, server, url, distribution, version, build, python, abi, platform):
        super(WheelMetadata, self).__init__(server, url, distribution, version, build, python, abi, platform)
        self._pkg_type = PackageTypes.WHEEL


class PackageTypes(object):
    WHEEL = "Wheel"
    TARBALL = "Tarball"
    EGG = "Egg"


class HttpRequestException(Exception): pass


class UnknownPackageTypeException(Exception): pass


class PackageNotAvailableException(Exception): pass
