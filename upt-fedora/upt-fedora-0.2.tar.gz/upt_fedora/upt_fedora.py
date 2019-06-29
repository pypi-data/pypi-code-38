# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import datetime

import jinja2
import upt


class FedoraPackage(object):
    def __init__(self, upt_pkg, output_dir):
        self.upt_pkg = upt_pkg

    def create(self):
        env = self._setup_jinja2()
        template = env.get_template(self.template)
        return template.render(pkg=self)

    def _setup_jinja2(self):
        env = jinja2.Environment(
            loader=jinja2.PackageLoader('upt_fedora', 'templates'),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )
        env.filters['reqformat'] = self.jinja2_reqformat
        return env

    def __getattribute__(self, name):
        if name in ['homepage', 'summary', 'version']:
            return self.upt_pkg.__getattribute__(name)
        else:
            return object.__getattribute__(self, name)

    @staticmethod
    def today():
        '''Return today's date well formatted for a Fedora changelog'''
        return datetime.datetime.today().strftime('%a %b %d %Y')

    @property
    def licenses(self):
        # See the Fedora licensing documentation at
        # https://fedoraproject.org/wiki/Licensing
        bad_licenses = [
            # These are SPDX identifiers
            'Aladdin',
            'APL-1.0',
            'Artistic-1.0',
            'Artistic-1.0-Perl',
            'EUPL-1.0',
            'Frameworx-1.0',
            'Intel',
            'OCLC-2.0',
            'RPL-1.5',
            'Watcom-1.0',
            'Xnet',
        ]

        spdx_identifiers = [
            upt_license.spdx_identifier
            for upt_license in self.upt_pkg.licenses
        ]

        if any([spdx_identifier in bad_licenses
                for spdx_identifier in spdx_identifiers]):
            return f'BAD LICENSE ({" ".join(spdx_identifiers)})'

        spdx2fedora = {
            # Upt licenses that have no Fedora equivalent are commented out.
            # 'AFL-1.1'
            # 'AFL-1.2'
            # 'AFL-2.0'
            # 'AFL-2.1'
            'AFL-3.0': 'AFL',
            'Apache-1.0': 'ASL 1.0',
            'Apache-1.1': 'ASL 1.1',
            'Apache-2.0': 'ASL 2.0',
            # 'APSL-1.0'
            # 'APSL-1.1'
            # 'APSL-1.2'
            'APSL-2.0': 'APSL 2.0',
            'Artistic-2.0': 'Artistic 2.0',
            'AAL': 'AAL',
            'BSD-2-Clause': 'BSD',
            'BSD-3-Clause': 'BSD',
            'CC0-1.0': 'CC0',
            'CECILL-B': 'CeCILL-B',
            'CECILL-C': 'CeCILL-C',
            'CECILL-2.1': 'CeCILL',
            'ClArtistic': 'Artistic clarified',
            'CNRI-Python': 'CNRI',
            'CDDL-1.0': 'CDDL-1.0',
            'CPL-1.0': 'CPL',
            'CPAL-1.0': 'CPAL',
            'CATOSL-1.1': 'CATOSL',
            'CUA-OPL-1.0': 'MPLv1.1',
            'EUDatagrid': 'EU Datagrid',
            'EPL-1.0': 'EPL-1.0',
            'EPL-2.0': 'EPL-2.0',
            'eCos-2.0': 'eCos',
            'ECL-2.0': 'ECL 2.0',
            'EFL-2.0': 'EFL 2.0',
            'Entessa': 'Entessa',
            'EUPL-1.1': 'EUPL 1.1',
            # 'EUPL-1.2'
            'Fair': 'Fair',
            # '0BSD'
            'AGPL-3.0-only': 'AGPLv3',
            'AGPL-3.0-or-later': 'AGPLv3+',
            'GFDL-1.1': 'GFDL',
            'GFDL-1.2': 'GFDL',
            'GFDL-1.3': 'GFDL',
            'GPL-2.0-only': 'GPLv2',
            'GPL-2.0-or-later': 'GPLv2+',
            'GPL-3.0': 'GPLv3',
            'GPL-3.0-or-later': 'GPLv3+',
            'LGPL-2.0-only': 'LGPLv2',
            'LGPL-2.0-or-later': 'LGPLv2+',
            'LGPL-2.1-only': 'LGPLv2',
            'LGPL-2.1-or-later': 'LGPLv2+',
            'LGPL-3.0-only': 'LGPLv3',
            'LGPL-3.0-or-later': 'LGPLv3+',
            # 'HPND'
            'IPL-1.0': 'IBM',
            'IPA': 'IPA',
            'ISC': 'ISC',
            'LPPL-1.3c': 'LPPL',
            # 'LiLiQ-P-1.1'
            # 'LiLiQ-R-version 1.'
            # 'LiLiQ-Rplus-1.1'
            'LPL-1.02': 'LPL',
            'MirOS': 'MirOS',
            'MS-PL': 'MS-PL',
            'MS-RL': 'MS-RL',
            'MIT': 'MIT',
            'Motosoto': 'Motosoto',
            'MPL-1.0': 'MPLv1.0',
            'MPL-1.1': 'MPLv1.1',
            'MPL-2.0': 'MPLv2.0',
            # 'Multics'
            'Naumen': 'Naumen',
            'NGPL': 'NGPL',
            'NPL-1.0': 'NPL',
            # 'NPL-1.1'
            'Nokia': 'Nokia',
            # 'NPOSL-3.0'
            # 'OGTSL'
            'OSL-3.0': 'OSL 3.0',
            'OpenSSL': 'OpenSSL',
            # 'OSET-PL-2.1'
            'PHP-3.0': 'PHP',
            'PostgreSQL': 'PostgreSQL',
            'Python-2.0': 'Python',
            'QPL-1.0': 'QPL',
            'RPSL-1.0': 'RPSL',
            # 'RSCPL'
            'Ruby': 'Ruby',
            'OFL-1.1': 'OFL',
            # 'SimPL-2.0'
            'Sleepycat': 'Sleepycat',
            'SISSL': 'SISSL',
            'SPL-1.0': 'SPL',
            'NCSA': 'NCSA',
            # 'UPL'
            'VSL-1.0': 'VSL',
            'W3C': 'W3C',
            'wxWindows': 'wxWindows',
            'ZPL-2.0': 'ZPLv2.0',
            'zlib': 'zlib',
            'zlib-acknowledgement': 'zlib with acknowledgement',
        }
        return ' '.join([spdx2fedora.get(spdx_identifier, 'TODO')
                         for spdx_identifier in spdx_identifiers])

    def depends(self, phase):
        return self.upt_pkg.requirements.get(phase, [])

    @property
    def build_depends(self):
        return self.depends('build')

    @property
    def run_depends(self):
        return self.depends('run')

    @property
    def test_depends(self):
        return self.depends('test')


class FedoraPythonPackage(FedoraPackage):
    '''Fedora Package for a Python package

    See https://fedoraproject.org/wiki/Packaging:Python
    '''
    template = 'python.spec'

    @property
    def name(self):
        return f'python-{self._sourcename(self.upt_pkg.name)}'

    @property
    def sourcename(self):
        return self._sourcename(self.upt_pkg.name)

    @property
    def source0(self):
        return '%pypi_source'

    @staticmethod
    def _sourcename(pkgname):
        if pkgname.startswith('python-'):
            return pkgname[7:]
        else:
            return pkgname

    def jinja2_reqformat(self, req, language_version=None):
        assert language_version in (2, 3)
        if language_version == 3:
            language_version = '%{python3_pkgversion}'

        name = self._sourcename(req.name)
        if req.specifier:
            return f'python{language_version}-{name} {req.specifier}'
        else:
            return f'python{language_version}-{name}'


class FedoraRubyPackage(FedoraPackage):
    '''Fedora Package for a Ruby Gem

    See https://fedoraproject.org/wiki/Packaging:Ruby?rd=Packaging/Ruby .
    '''
    template = 'ruby.spec'

    @property
    def name(self):
        return 'rubygem-%{gem_name}'

    @property
    def source0(self):
        return 'https://rubygems.org/gems/%{gem_name}-%{version}.gem'

    @property
    def sourcename(self):
        return self.upt_pkg.name

    def jinja2_reqformat(self, req):
        if req.specifier:
            return f'rubygem({req.name}) {req.specifier}'
        else:
            return f'rubygem({req.name})'


class FedoraBackend(upt.Backend):
    name = 'fedora'

    def create_package(self, upt_pkg, output=None):
        pkg_classes = {
            'pypi': FedoraPythonPackage,
            'rubygems': FedoraRubyPackage,
        }

        try:
            pkg_cls = pkg_classes[upt_pkg.frontend]
        except KeyError:
            raise upt.UnhandledFrontendError(self.name, upt_pkg.frontend)

        fedora_pkg = pkg_cls(upt_pkg, output)
        print(fedora_pkg.create())
