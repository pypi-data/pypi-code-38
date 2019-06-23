# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import json
import pkg_resources
import re
import tempfile
from urllib.request import urlretrieve
import zipfile

import requests
import upt

from .licenses import guess_licenses


class PyPIPackage(upt.Package):
    pass


class PyPIFrontend(upt.Frontend):
    name = 'pypi'

    @staticmethod
    def get_archive_info(release, kind):
        for elt in release:
            if elt['packagetype'] == kind:
                digests = elt.get('digests', {})
                return (elt['url'], elt.get('size', 0),
                        digests.get('md5'), digests.get('sha256'))
        raise ValueError(f'No archive of type "{kind}" could be found')

    def get_sdist_archive_url(self, release):
        url, _, _, _ = self.get_archive_info(release, 'sdist')
        return url

    def get_wheel_url(self, release):
        url, _, _, _ = self.get_archive_info(release, 'bdist_wheel')
        return url

    @staticmethod
    def _string_req_to_upt_pkg_req(string_req):
        r = pkg_resources.Requirement.parse(string_req)
        name = r.project_name
        specifier = ','.join(op+version for (op, version) in r.specs)
        return upt.PackageRequirement(name, specifier)

    @classmethod
    def _string_req_list_to_upt_pkg_req_list(cls, string_req_list):
        return [cls._string_req_to_upt_pkg_req(s) for s in string_req_list]

    @classmethod
    def compute_requirements_from_metadata_json(cls, json_file):
        requirements = {}
        parse_method = cls._string_req_list_to_upt_pkg_req_list
        try:
            with open(json_file) as f:
                j = json.load(f)
                for reqs in j.get('run_requires', []):
                    if list(reqs.keys()) != ['requires']:
                        continue
                    requirements['run'] = parse_method(reqs['requires'])
                for reqs in j.get('test_requires', []):
                    if list(reqs.keys()) != ['requires']:
                        continue
                    requirements['test'] = parse_method(reqs['requires'])
        except json.JSONDecodeError:
            return {}

        return requirements

    @classmethod
    def compute_requirements_from_wheel(cls, wheel_url):
        with tempfile.NamedTemporaryFile() as wheel,\
             tempfile.TemporaryDirectory() as d:
            urlretrieve(wheel_url, wheel.name)
            dirname = '-'.join(wheel_url.rsplit('/', 1)[-1].split('-', 2)[:2])
            dirname += '.dist-info'
            z = zipfile.ZipFile(wheel.name)
            try:
                z.extract(f'{dirname}/metadata.json', d)
                return cls.compute_requirements_from_metadata_json(
                    f'{d}/{dirname}/metadata.json')
            except KeyError:
                # No metadata.json in this wheel
                return {}

    def compute_requirements(self):
        """Computes the requirements using various methods.

        Try to compute the requirements of the package by;
        - looking at the requires_dist field of the JSON document we are
          parsing.
        - downloading and opening the wheel from this release, then reading the
          metadata.json file inside.
        """
        reqs = {}
        run_reqs = []
        test_reqs = []
        for req in self.json.get('info', {}).get('requires_dist', []) or []:
            try:
                req_name, extra = req.split(';')
                extra = extra.strip()
            except ValueError:
                # No "extras".
                req_name = req
                extra = None

            pkg = self._string_req_to_upt_pkg_req(req_name)
            if extra is not None:
                # We only care about extras if they are likely to define the
                # test requirements.
                # TODO: care about optional runtime requirements when upt
                # provides support for them.
                # TODO: handle cases where 'extra' matches a requirement on the
                # Python version.
                m = re.match("extra == '(.*)'", extra)
                if m:
                    extra_name = m.group(1)
                    if extra_name in ('test', 'tests', 'testing'):
                        test_reqs.append(pkg)
            else:
                run_reqs.append(pkg)

        if run_reqs and test_reqs:
            # We got both the runtime and test requirements.
            reqs['run'] = run_reqs
            reqs['test'] = test_reqs
        else:
            # We probably missed some of the requirements, let's see whether
            # we are more lucky with the wheel.
            try:
                version = self.json['info']['version']
                wheel_url = self.get_wheel_url(self.json['releases'][version])
                wheel_reqs = self.compute_requirements_from_wheel(wheel_url)
            except ValueError:
                # No wheel for this package.
                wheel_reqs = {}
            finally:
                run_reqs = run_reqs or wheel_reqs.get('run')
                test_reqs = test_reqs or wheel_reqs.get('test')
                if run_reqs:
                    reqs['run'] = run_reqs
                if test_reqs:
                    reqs['test'] = test_reqs

        return reqs

    def get_archives(self, release):
        url, size, md5, sha256 = self.get_archive_info(release, 'sdist')
        archive = upt.Archive(url, size=size, md5=md5, sha256=sha256)
        return [archive]

    def parse(self, pkg_name):
        url = f'https://pypi.org/pypi/{pkg_name}/json'
        r = requests.get(url)
        if not r.ok:
            raise upt.InvalidPackageNameError(self.name, pkg_name)
        self.json = r.json()
        version = self.json['info']['version']
        requirements = self.compute_requirements()
        try:
            self.archives = self.get_archives(self.json['releases'][version])
            sdist_url = self.archives[0].url
        except ValueError:
            self.archives = []
            sdist_url = ''
        d = {
            'homepage': self.json['info']['home_page'],
            'summary': self.json['info']['summary'],
            'description': self.json['info']['description'],
            'requirements': requirements,
            'archives': self.archives,
            'licenses': guess_licenses(self.json, sdist_url),
        }
        return PyPIPackage(pkg_name, version, **d)
