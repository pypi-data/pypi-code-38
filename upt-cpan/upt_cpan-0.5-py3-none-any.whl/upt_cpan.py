# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import requests
import upt


class CPANPackage(upt.Package):
    pass


class CPANFrontend(upt.Frontend):
    name = 'cpan'

    def _get_homepage(self, json_resources):
        homepage = json_resources.get('homepage')
        if homepage is None:
            for kind in ('bugtracker', 'repository'):
                d = json_resources.get(kind, {})
                homepage = d.get('web')
                if homepage is not None:
                    break
        return homepage

    def _get_licenses(self, licenses):
        # List taken from https://metacpan.org/pod/CPAN::Meta::Spec#license .
        # Not included here:
        # - gpl_1: deprecated for ages
        # - ssleay: not even listed on https://spdx.org/licenses/
        # - open_source: not a real license
        # - restricte: not a real license
        # - unrestricte: not a real license
        # - unknown: not a real license
        metacpan_licenses = {
            'agpl_3':
                upt.licenses.GNUAfferoGeneralPublicLicenseThreeDotZeroPlus,
            'apache_1_1': upt.licenses.ApacheLicenseOneDotOne,
            'apache_2_0': upt.licenses.ApacheLicenseTwoDotZero,
            'artistic_1': upt.licenses.ArtisticLicenseOneDotZero,
            'artistic_2': upt.licenses.ApacheLicenseTwoDotZero,
            'bsd': upt.licenses.BSDThreeClauseLicense,
            'freebsd': upt.licenses.BSDTwoClauseLicense,
            'gfdl_1_2': upt.licenses.GNUFreeDocumentationLicenseOneDotTwo,
            'gfdl_1_3': upt.licenses.GNUFreeDocumentationLicenseOneDotThree,
            'gpl_2': upt.licenses.GNUGeneralPublicLicenseTwo,
            'gpl_3': upt.licenses.GNUGeneralPublicLicenseThree,
            'lgpl_2_1': upt.licenses.GNULesserGeneralPublicLicenseTwoDotOne,
            'lgpl_3_0': upt.licenses.GNULesserGeneralPublicLicenseThreeDotZero,
            'mit': upt.licenses.MITLicense,
            'mozilla_1_0': upt.licenses.MozillaPublicLicenseOneDotZero,
            'mozilla_1_1': upt.licenses.MozillaPublicLicenseOneDotOne,
            'openssl': upt.licenses.OpenSSLLicense,
            'perl_5': upt.licenses.PerlLicense,
            'qpl_1_0': upt.licenses.QPublicLicenseOneDotZero,
            'sun': upt.licenses.SunIndustryStandardsSourceLicenceOneDotOne,
            'zlib': upt.licenses.ZlibLicense,
        }

        return [metacpan_licenses.get(l, upt.licenses.UnknownLicense)()
                for l in licenses]

    def _get_requirements(self, json_dependencies):
        phases_to_upt_phases = {
            'configure': 'config',
            'build': 'build',
            'runtime': 'run',
            'test': 'test',
        }

        requirements = {}
        for phase, dependencies in json_dependencies.items():
            # We do not really care about this phase.
            if phase == 'develop':
                continue

            upt_phase = phases_to_upt_phases.get(phase, None)
            if upt_phase is None:
                continue

            requirements[upt_phase] = [
                upt.PackageRequirement(module,
                                       '' if spec == '0' else f'>={spec}')
                for (module, spec) in dependencies.get('requires', {}).items()
                if module != 'perl'  # This seems implicit
            ]

        return requirements

    def _get_archives(self, json):
        try:
            url = json['download_url']
            stat = json.get('stat', {})
            return [
                upt.Archive(url=url, size=stat.get('size', 0))
            ]
        except KeyError:
            return []

    def parse(self, pkg_name):
        # The following document https://metacpan.org/pod/CPAN::Meta::Spec
        # is quite useful to understand the JSON we get.
        release_name = pkg_name.replace('::', '-')
        url = f'https://fastapi.metacpan.org/v1/release/{release_name}'
        r = requests.get(url)
        if not r.ok:
            raise upt.InvalidPackageNameError(self.name, pkg_name)
        json = r.json()

        metadata = json.get('metadata', {})
        version = metadata.get('version', '')
        homepage = self._get_homepage(json.get('resources', {}))

        pkg_args = {
            'summary': json.get('abstract', ''),
            'homepage': homepage,
            'licenses': self._get_licenses(json.get('license', [])),
            'archives': self._get_archives(json),
            'requirements': self._get_requirements(metadata.get('prereqs', {}))
        }
        return CPANPackage(pkg_name, version, **pkg_args)
