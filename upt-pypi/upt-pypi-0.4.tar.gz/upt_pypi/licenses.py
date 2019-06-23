# Copyright 2018-2019 Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import tarfile
import tempfile
from urllib.request import urlretrieve
import zipfile

import upt


DEFAULT_LICENSE = upt.licenses.UnknownLicense


def guess_licenses_using_classifiers(classifiers):
    # All available license classifiers provided by PyPI.
    # TODO: Update the list once
    # https://github.com/pypa/warehouse/issues/2996 has been fixed.
    all_license_classifiers = {
        'License :: Aladdin Free Public License (AFPL)':
            upt.licenses.AladdinFreePublicLicense,
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication':
            upt.licenses.CC0LicenceOneDotZero,
        'License :: CeCILL-B Free Software License Agreement (CECILL-B)':
            upt.licenses.CeCILLBLicense,
        'License :: CeCILL-C Free Software License Agreement (CECILL-C)':
            upt.licenses.CeCILLCLicense,
        'License :: Eiffel Forum License (EFL)':
            upt.licenses.EiffelForumLicenseTwoDotZero,
        'License :: Nokia Open Source License (NOKOS)':
            upt.licenses.NokiaOpenSourceLicense,
        'License :: OSI Approved :: Attribution Assurance License':
            upt.licenses.AttributionAssuranceLicense,
        'License :: OSI Approved :: Boost Software License 1.0 (BSL-1.0)':
            upt.licenses.BoostSoftwareLicense,
        'License :: OSI Approved :: CEA CNRS Inria Logiciel Libre License, version 2.1 (CeCILL-2.1)': # noqa
            upt.licenses.CeCILLTwoDotOne,
        'License :: OSI Approved :: Common Development and Distribution License 1.0 (CDDL-1.0)': # noqa
            upt.licenses.CommonDevelopmentAndDistributionLicenseOneDotZero,
        'License :: OSI Approved :: Common Public License':
            upt.licenses.CommonPublicLicenseOneDotZero,
        'License :: OSI Approved :: Eclipse Public License 1.0 (EPL-1.0)':
            upt.licenses.EclipsePublicLicenseOneDotZero,
        'License :: OSI Approved :: Eiffel Forum License':
            upt.licenses.EiffelForumLicenseTwoDotZero,
        'License :: OSI Approved :: European Union Public Licence 1.0 # (EUPL 1.0)': # noqa
            upt.licenses.EuropeanUnionPublicLicenseOneDotZero,
        'License :: OSI Approved :: European Union Public Licence 1.1 (EUPL 1.1)': # noqa
            upt.licenses.EuropeanUnionPublicLicenseOneDotOne,
        'License :: OSI Approved :: GNU Affero General Public License v3':
            upt.licenses.GNUAfferoGeneralPublicLicenseThreeDotZero,
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)': # noqa
            upt.licenses.GNUAfferoGeneralPublicLicenseThreeDotZeroPlus,
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)':
            upt.licenses.GNUGeneralPublicLicenseTwo,
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)': # noqa
            upt.licenses.GNUGeneralPublicLicenseTwoPlus,
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)':
            upt.licenses.GNUGeneralPublicLicenseThree,
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)': # noqa
            upt.licenses.GNUGeneralPublicLicenseThreePlus,
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)': # noqa
            upt.licenses.GNULesserGeneralPublicLicenseThreeDotZero,
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)': # noqa
            upt.licenses.GNULesserGeneralPublicLicenseThreeDotZeroPlus,
        'License :: OSI Approved :: IBM Public License':
            upt.licenses.IBMPublicLicense,
        'License :: OSI Approved :: Intel Open Source License':
            upt.licenses.IntelOpenSourceLicense,
        'License :: OSI Approved :: ISC License (ISCL)':
            upt.licenses.ISCLicense,
        # XXX: not available in upt
        # 'License :: OSI Approved :: Jabber Open Source License'
        'License :: OSI Approved :: MIT License':
            upt.licenses.MITLicense,
        # XXX: not available in upt
        # 'License :: OSI Approved :: MITRE Collaborative Virtual Workspace License (CVW)' # noqa
        'License :: OSI Approved :: Motosoto License':
            upt.licenses.MotosotoLicense,
        'License :: OSI Approved :: Mozilla Public License 1.0 (MPL)':
            upt.licenses.MozillaPublicLicenseOneDotZero,
        'License :: OSI Approved :: Mozilla Public License 1.1 (MPL 1.1)':
            upt.licenses.MozillaPublicLicenseOneDotOne,
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)':
            upt.licenses.MozillaPublicLicenseTwoDotZero,
        'License :: OSI Approved :: Nethack General Public License':
            upt.licenses.NethackGeneralPublicLicense,
        'License :: OSI Approved :: Nokia Open Source License':
            upt.licenses.NokiaOpenSourceLicense,
        'License :: OSI Approved :: Open Group Test Suite License':
            upt.licenses.OpenGroupTestSuiteLicense,
        'License :: OSI Approved :: Python License (CNRI Python License)':
            upt.licenses.CNRIPythonLicense,
        'License :: OSI Approved :: Python Software Foundation License':
            upt.licenses.PythonLicenseTwoDotZero,
        'License :: OSI Approved :: Qt Public License (QPL)':
            upt.licenses.QPublicLicenseOneDotZero,
        'License :: OSI Approved :: Ricoh Source Code Public License':
            upt.licenses.RicohSourceCodePublicLicense,
        'License :: OSI Approved :: Sleepycat License':
            upt.licenses.SleepycatLicense,
        'License :: OSI Approved :: Sun Industry Standards Source License (SISSL)': # noqa
            upt.licenses.SunIndustryStandardsSourceLicenceOneDotOne,
        'License :: OSI Approved :: Sun Public License':
            upt.licenses.SunPublicLicense,
        'License :: OSI Approved :: Universal Permissive License (UPL)':
            upt.licenses.UniversalPermissiveLicense,
        'License :: OSI Approved :: University of Illinois/NCSA Open Source License': # noqa
            upt.licenses.NCSALicense,
        'License :: OSI Approved :: Vovida Software License 1.0':
            upt.licenses.VovidaSoftwareLicenseVOneDotZero,
        'License :: OSI Approved :: W3C License':
            upt.licenses.W3CLicense,
        'License :: OSI Approved :: X.Net License':
            upt.licenses.XNetLicense,
        'License :: OSI Approved :: zlib/libpng License':
            upt.licenses.ZlibLibpngLicense,
        'License :: OSI Approved :: Zope Public License':
            upt.licenses.ZopePublicLicenseTwoDotZero,
    }

    not_actual_licenses = [
        # These are licenses, but the version is not clearly specified.
        # NPL: 1.0 or 1.1?
        'License :: Netscape Public License (NPL)',
        # AFL: is it 1.1, 1.2, 2.0, 2.1 or 3.0?
        'License :: OSI Approved :: Academic Free License (AFL)',
        # ASL: is it 1.0, 1.1 or 2.0?
        'License :: OSI Approved :: Apache Software License',
        # APSL: is it 1.0, 1.1, 1.2 or 2.0?
        'License :: OSI Approved :: Apple Public Source License',
        # Artistic License: is it 1.0 or 2.0?
        'License :: OSI Approved :: Artistic License',
        # BSD: what version?
        'License :: OSI Approved :: BSD License',
        # FDL: what version?
        'License :: OSI Approved :: GNU Free Documentation License (FDL)',
        # GPL: what version?
        'License :: OSI Approved :: GNU General Public License (GPL)',
        # LGPLv2: v2.0 or v2.1?
        'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)', # noqa
        # LGPLv2+: v2.0+ or v2.1+?
        'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)', # noqa
        # 'LGPL' without a version: what version are we talking about?
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)', # noqa
        # These are not actual licenses.
        'License :: DFSG approved',
        'License :: OSI Approved',
        'License :: Free For Educational Use',
        'License :: Free For Home Use',
        'License :: Free for non-commercial use',
        'License :: Freely Distributable',
        'License :: Free To Use But Restricted',
        'License :: Freeware',
        'License :: Other/Proprietary License',
        'License :: Public Domain',
        'License :: Repoze Public License',
    ]

    found = [all_license_classifiers.get(c, DEFAULT_LICENSE)()
             for c in classifiers
             if c.startswith('License ::')
             and c not in not_actual_licenses]
    return found


def guess_licenses_using_license_field(license_field):
    # Is this a valid SPDX identifier? One can always dream.
    spdx = upt.licenses.get_license_by_spdx_identifier(license_field)
    if not isinstance(spdx, DEFAULT_LICENSE):
        return [spdx]

    # Let's look at the most used fields on PyPI.
    # First, we "normalize" the value. "MIT" and "mit" are the same thing.
    # Just like "GPL3", "GPL-3" and "gpl3".
    license_field = license_field.replace('\n', '')
    license_field = license_field.replace('\r', '')
    license_field = license_field.replace(' ', '')
    license_field = license_field.replace('-', '')
    license_field = license_field.lower()

    pypi_stats = {
        'mit': upt.licenses.MITLicense,
        'mitlicense': upt.licenses.MITLicense,
        'agpl3': upt.licenses.GNUAfferoGeneralPublicLicenseThreeDotZero,
        'gplv3': upt.licenses.GNUGeneralPublicLicenseThree,
        'apache2.0': upt.licenses.ApacheLicenseTwoDotZero,
        'apachelicense2.0': upt.licenses.ApacheLicenseTwoDotZero,
        'apachelicense,version2.0': upt.licenses.ApacheLicenseTwoDotZero,
        'gpl3': upt.licenses.GNUGeneralPublicLicenseThree,
        'gplv2': upt.licenses.GNUGeneralPublicLicenseTwo,
        'gplv3+': upt.licenses.GNUGeneralPublicLicenseThreePlus,
        'bsd3clause': upt.licenses.BSDThreeClauseLicense,
        'zpl2.1': upt.licenses.ZopePublicLicenseTwoDotOne,
        'apache2': upt.licenses.ApacheLicenseTwoDotZero,
        'lgplv3': upt.licenses.GNULesserGeneralPublicLicenseThreeDotZero,
        'lgpl3': upt.licenses.GNULesserGeneralPublicLicenseThreeDotZero,
        'gpl3.0': upt.licenses.GNUGeneralPublicLicenseThree,
        'isc': upt.licenses.ISCLicense,
        'gnugplv3': upt.licenses.GNUGeneralPublicLicenseThree,
        'apachesoftwarelicense2.0': upt.licenses.ApacheLicenseTwoDotZero,
        'gpl2': upt.licenses.GNUGeneralPublicLicenseTwo,
        'agplv3': upt.licenses.GNUAfferoGeneralPublicLicenseThreeDotZero,
        'wtfpl': upt.licenses.WTFPLicense,
        'bsd3': upt.licenses.BSDThreeClauseLicense,
        'bsd3clauselicense': upt.licenses.BSDThreeClauseLicense,
        'gnugeneralpubliclicensev3': upt.licenses.GNUGeneralPublicLicenseThree,
        # 'zpl':  # Missing version
        'gplversion2': upt.licenses.GNUGeneralPublicLicenseTwo,
        'apachelicenseversion2.0': upt.licenses.ApacheLicenseTwoDotZero,
        'mitlicence': upt.licenses.MITLicense,
        'gplv2+': upt.licenses.GNUGeneralPublicLicenseTwoPlus,
        'newbsd': upt.licenses.BSDThreeClauseLicense,
        'mpl2.0': upt.licenses.MozillaPublicLicenseTwoDotZero,
        'http://www.apache.org/licenses/license2.0':
            upt.licenses.ApacheLicenseTwoDotZero,
        'bsd2clause': upt.licenses.BSDTwoClauseLicense,
        'agpl3.0': upt.licenses.GNUAfferoGeneralPublicLicenseThreeDotZero,
        'newbsdlicense': upt.licenses.BSDThreeClauseLicense,
        'themitlicense': upt.licenses.MITLicense,
        # 'bsdderived(http://www.repoze.org/license.txt)':
        'apachelicense(2.0)': upt.licenses.ApacheLicenseTwoDotZero,
        # 'apachelicense':  # Missing versino
        'gnugeneralpubliclicensev3(gplv3)':
            upt.licenses.GNUGeneralPublicLicenseThree,
        'themitlicense(mit)': upt.licenses.MITLicense,
        'license::osiapproved::mitlicense': upt.licenses.MITLicense,
        'gnugeneralpubliclicensev3.0':
            upt.licenses.GNUGeneralPublicLicenseThree,
        # 'creativecommonsattributionnoncommercialsharealikelicense':  # v4.0?
        # 'gnugeneralpubliclicense':  # Missing version
        'lgplv3+': upt.licenses.GNULesserGeneralPublicLicenseThreeDotZeroPlus,
        '3clausebsd': upt.licenses.BSDThreeClauseLicense,
        'agplv3+': upt.licenses.GNUAfferoGeneralPublicLicenseThreeDotZeroPlus,
        # 'gnugeneralpubliclicense(gpl)':  # Missing version
        # 'mpl':  # Missing version
        # 'proprietary':
        'iscl': upt.licenses.ISCLicense,
        'simplifiedbsd': upt.licenses.BSDTwoClauseLicense,
        'gnugplv2': upt.licenses.GNUGeneralPublicLicenseTwo,
        'gpl3+': upt.licenses.GNUGeneralPublicLicenseThreePlus,
        'apachev2': upt.licenses.ApacheLicenseTwoDotZero,
        'lgpl3.0': upt.licenses.GNULesserGeneralPublicLicenseThreeDotZero,
        'bsd2clauselicense': upt.licenses.BSDTwoClauseLicense,
        'gnugeneralpubliclicensev3orlater(gplv3+)':
            upt.licenses.GNUGeneralPublicLicenseThreePlus,
        'bsd(3clause)': upt.licenses.BSDThreeClauseLicense,
        # 'python':  # Missing version
        # 'license::osiapproved::apachesoftwarelicense':  # Missing version
        'bsd2': upt.licenses.BSDTwoClauseLicense,
        'cc0': upt.licenses.CC0LicenceOneDotZero,
        'apachev2.0': upt.licenses.ApacheLicenseTwoDotZero,
        # 'gnulgpl':  # Missing version
        'mpl2': upt.licenses.MozillaPublicLicenseTwoDotZero,
        'isclicense': upt.licenses.ISCLicense,
        'gnugeneralpubliclicenseversion3':
            upt.licenses.GNUGeneralPublicLicenseThree,
        # 'gpllicense,seelicense':  # Missing version
        'gnugpl3': upt.licenses.GNUGeneralPublicLicenseThree,
        'apache2.0license': upt.licenses.ApacheLicenseTwoDotZero,
        'lgplv2+': upt.licenses.GNULesserGeneralPublicLicenseTwoDotZeroPlus,
        # 'pythonsoftwarefoundationlicense':  # Missing version
        # 'gplv2.1':  # Does this even exist?
        'modifiedbsd': upt.licenses.BSDThreeClauseLicense,
        'simplifiedbsdlicense': upt.licenses.BSDTwoClauseLicense,
        'mozillapubliclicense2.0(mpl2.0)':
            upt.licenses.MozillaPublicLicenseTwoDotZero,
        'gpl3.0+': upt.licenses.GNUGeneralPublicLicenseThreePlus,
        'lgplv2': upt.licenses.GNULesserGeneralPublicLicenseTwoDotZero,
        'gpl2.0': upt.licenses.GNUGeneralPublicLicenseTwo,
        'apachelicensev2.0': upt.licenses.ApacheLicenseTwoDotZero,
        'gnuafferogeneralpubliclicensev3':
            upt.licenses.GNUAfferoGeneralPublicLicenseThreeDotZero,
        'gnulessergeneralpubliclicensev3orlater(lgplv3+)':
            upt.licenses.GNULesserGeneralPublicLicenseThreeDotZeroPlus,
        'gnuagplv3':
            upt.licenses.GNUAfferoGeneralPublicLicenseThreeDotZero,
        'gpl2+': upt.licenses.GNUGeneralPublicLicenseTwoPlus,
        'asl2.0': upt.licenses.ApacheLicenseTwoDotZero,
        'http://www.apache.org/licenses/license2.0.html':
            upt.licenses.ApacheLicenseTwoDotZero,
        'gnugeneralpubliclicensev2(gplv2)':
            upt.licenses.GNUGeneralPublicLicenseTwo,
        # 'beerware'
        'http://opensource.org/licenses/mit': upt.licenses.MITLicense,
        'http://www.opensource.org/licenses/mitlicense.php':
            upt.licenses.MITLicense,
        'freebsd': upt.licenses.BSDTwoClauseLicense,
        'cecillb': upt.licenses.CeCILLBLicense,
        'gplv3orlater': upt.licenses.GNUGeneralPublicLicenseThreePlus,
        'lgplv2.1': upt.licenses.GNULesserGeneralPublicLicenseTwoDotOne,
        'lgpl2.1': upt.licenses.GNULesserGeneralPublicLicenseTwoDotOne,
        'apachelicensev2': upt.licenses.ApacheLicenseTwoDotZero,
        'gplv3.0': upt.licenses.GNUGeneralPublicLicenseThree,
        'bsdnew': upt.licenses.BSDThreeClauseLicense,
        # 'license::osiapproved::bsdlicense'
        'mplv2.0': upt.licenses.MozillaPublicLicenseTwoDotZero,
        'gnugeneralpubliclicensev2orlater(gplv2+)':
            upt.licenses.GNUGeneralPublicLicenseTwoPlus,
        'gnuafferogeneralpubliclicensev3orlater(agplv3+)':
            upt.licenses.GNUAfferoGeneralPublicLicenseThreeDotZeroPlus,
        'mplv2': upt.licenses.MozillaPublicLicenseTwoDotZero,
        # 'mit/apache2.0':
        # 'mit/x'
        '2clausebsd': upt.licenses.BSDTwoClauseLicense,
        'gnulessergeneralpubliclicensev3(lgplv3)':
            upt.licenses.GNULesserGeneralPublicLicenseThreeDotZero,
        'gnulessergeneralpubliclicense(lgpl),version3':
            upt.licenses.GNULesserGeneralPublicLicenseThreeDotZero,
        # 'psfl'  # Missing version
        'apachelicenseversion2': upt.licenses.ApacheLicenseTwoDotZero,
        # 'alv2'
        'gplversion3': upt.licenses.GNUGeneralPublicLicenseThree,
        'gnugplv3+': upt.licenses.GNUGeneralPublicLicenseThreePlus,
        'revisedbsdlicense': upt.licenses.BSDThreeClauseLicense,
        # 'unlicensed'
        # 'mit/x11'
        # 'gpllicense'  # Missing versino
        'gnugplv3.0': upt.licenses.GNUGeneralPublicLicenseThree,
        'gplv3license': upt.licenses.GNUGeneralPublicLicenseThree,
        # 'gnulibraryorlessergeneralpubliclicense(lgpl)'  # Missing version
        'gnuafferogeneralpubliclicense,version3':
            upt.licenses.GNUAfferoGeneralPublicLicenseThreeDotZero,
        # 'gnulessergeneralpubliclicense'  # Missing version
        # 'other/proprietarylicense'
        'gnugeneralpubliclicensev2':
            upt.licenses.GNUGeneralPublicLicenseTwo,
        'agpl3+':
            upt.licenses.GNUAfferoGeneralPublicLicenseThreeDotZeroPlus,
        'lgpl2.1+':
            upt.licenses.GNULesserGeneralPublicLicenseTwoDotOnePlus,
        'mozillapubliclicenseversion2.0':
            upt.licenses.MozillaPublicLicenseTwoDotZero,
        # 'gnugeneralpubliclicence'  # Missing version
        'apachelicense2': upt.licenses.ApacheLicenseTwoDotZero,
        'gnugplversion3': upt.licenses.GNUGeneralPublicLicenseThree,
        # 'free'
        # 'copying'
        # 'bsdlike'
        'apachev2.0license': upt.licenses.ApacheLicenseTwoDotZero,
        # 'expatlicense':
        'gnulgplv3': upt.licenses.GNUGeneralPublicLicenseThree,
        'zlib': upt.licenses.ZlibLicense,
        'apachesoftwarelicensev2': upt.licenses.ApacheLicenseTwoDotZero,
        # 'bsdlicence,seelicensefile'
        'apache2license': upt.licenses.ApacheLicenseTwoDotZero,
        # 'gnuv3'  # GPL, LGPL?
        # 'artisticlicense2.0+forcedfairplayconstraints'
        # 'cecill'  # Missing version
        # 'osi'
        'lgplv2.1+':
            upt.licenses.GNULesserGeneralPublicLicenseTwoDotOnePlus,
        # 'aplv2'
        'bsd3license': upt.licenses.BSDThreeClauseLicense,
        'apachelicence2.0': upt.licenses.ApacheLicenseTwoDotZero,
        # 'mitlicense,seelicense'
        # 'private'
        # 'gpl2.0/lgpl2.1'
        'gplv2.0': upt.licenses.GNUGeneralPublicLicenseTwo,
        # 'gnuafferogeneralpubliclicense'
        # 'proprietaryintel'
        # 'gnulessergeneralpubliclicense(lgpl)'  # Missing version
        'modifiedbsdlicense': upt.licenses.BSDThreeClauseLicense,
        'apachesoftwarelicensev2.0': upt.licenses.ApacheLicenseTwoDotZero,
        'agpl3.0orlater':
            upt.licenses.GNUAfferoGeneralPublicLicenseThreeDotZeroPlus,
        'lgplv3.0':
            upt.licenses.GNULesserGeneralPublicLicenseThreeDotZero,
        'mit(http://opensource.org/licenses/mit)': upt.licenses.MITLicense,
        'bsd3clause"new"or"revisedlicense"':
            upt.licenses.BSDThreeClauseLicense,
        # 'freeware'
        # 'apl2.0'
        # 'bsd(http://dev.2degreesnetwork.com/p/2degreeslicense.html)'
        # 'psl'
        # 'freefornoncommercialuse'
        'revisedbsd': upt.licenses.BSDThreeClauseLicense,
        'cc01.0': upt.licenses.CC0LicenceOneDotZero,
        'http://www.fsf.org/licensing/licenses/agpl3.0.html':
            upt.licenses.GNUAfferoGeneralPublicLicenseThreeDotZero,
        # 'psforzpl'
        # 'mitorapachelicense2.0':
        'bsd3clause"new"or"revised"license':
            upt.licenses.BSDThreeClauseLicense,
        # 'bsdlicence'
        # 'theunlicense'
        'gplv3oranylaterversion':
            upt.licenses.GNUGeneralPublicLicenseThreePlus,
        'gpl3.0orlater': upt.licenses.GNUGeneralPublicLicenseThreePlus,
        'https://www.gnu.org/licenses/gpl3.0.txt':
            upt.licenses.GNUGeneralPublicLicenseThree,
        # 'pythonlicense',
        'gnugeneralpubliclicense,version2':
            upt.licenses.GNUGeneralPublicLicenseTwo,
        'gnulessergeneralpubliclicensev3':
            upt.licenses.GNULesserGeneralPublicLicenseThreeDotZero,
        # 'asl'  # Missing version
        # 'https://aka.ms/azuremlsdklicense'
        'gnugeneralpubliclicenseversion2':
            upt.licenses.GNUGeneralPublicLicenseTwo,
        'boostsoftwarelicense1.0(bsl1.0)':
            upt.licenses.BoostSoftwareLicense,
        'https://www.gnu.org/licenses/agpl3.0.html':
            upt.licenses.GNUAfferoGeneralPublicLicenseThreeDotZero,
        'cecillv2': upt.licenses.CeCILLTwoDotZero,
        'license::osiapproved::gnugeneralpubliclicensev3(gplv3)':
            upt.licenses.GNUGeneralPublicLicenseThree,
        '3clausebsdlicense': upt.licenses.BSDThreeClauseLicense,
        'gnugplv2.0': upt.licenses.GNUGeneralPublicLicenseTwo,
        'gnugpl3.0': upt.licenses.GNUGeneralPublicLicenseThree,
        'mitlicense(seelicense)': upt.licenses.MITLicense,
        # 'apl2'
        'cecillc': upt.licenses.CeCILLCLicense,
        'gplv2orlater': upt.licenses.GNUGeneralPublicLicenseTwoPlus,
        'gnugplv2+': upt.licenses.GNUGeneralPublicLicenseTwoPlus,
        'mozillapubliclicense2.0':
            upt.licenses.MozillaPublicLicenseTwoDotZero,
        'zpl2.1(http://www.zope.org/resources/license/zpl2.1)':
            upt.licenses.ZopePublicLicenseTwoDotOne,
        'gnugeneralpubliclicensev2.0':
            upt.licenses.GNUGeneralPublicLicenseTwo,
        # 'afl'
        # 'expat'
        # 'proprietarylicense'
        'gnugeneralpubliclicense,version3':
            upt.licenses.GNUGeneralPublicLicenseThree,
        # 'mit/x11licensehttp://opensource.org/licenses/mit'
        'gnugpl2':
            upt.licenses.GNUGeneralPublicLicenseTwo,
        'gnugeneralpubliclicense(gpl),version3':
            upt.licenses.GNUGeneralPublicLicenseThree,
        'apacheversion2.0':
            upt.licenses.ApacheLicenseTwoDotZero,
        # 'asf'
        # 'lpgl,seelicensefile.
        'agplv3orlater':
            upt.licenses.GNUAfferoGeneralPublicLicenseThreeDotZeroPlus,
        '2clausebsdlicense':
            upt.licenses.BSDTwoClauseLicense,
        # mitbsd
        'mitlicence,seelicence.txt': upt.licenses.MITLicense,
        'lgpl3+': upt.licenses.GNULesserGeneralPublicLicenseThreeDotZeroPlus,
        'gnugplv2orlater': upt.licenses.GNUGeneralPublicLicenseTwoPlus,
        'gnugpl3orlater': upt.licenses.GNUGeneralPublicLicenseThreePlus,
        'isclicense(iscl)': upt.licenses.ISCLicense,
        'gnulgplv3+':
            upt.licenses.GNULesserGeneralPublicLicenseThreeDotZeroPlus,
        'apachelicense,version2': upt.licenses.ApacheLicenseTwoDotZero,
        'lgpl3.0+': upt.licenses.GNULesserGeneralPublicLicenseThreeDotZeroPlus,
        'gnu/gplv3': upt.licenses.GNUGeneralPublicLicenseThree,
        'postgresql': upt.licenses.PostgreSQLLicense,
        # gnulicense  # Missing version
        'eupl1.2': upt.licenses.EuropeanUnionPublicLicenseOneDotTwo,
        'gnugeneralpubliclicenseversion2,june1991':
            upt.licenses.GNUGeneralPublicLicenseTwo,
        'gnulessergeneralpubliclicensev3.0':
            upt.licenses.GNULesserGeneralPublicLicenseThreeDotZero,
        'cc01.0universal':
            upt.licenses.CC0LicenceOneDotZero,
        # mit(expat)
        # askforpermissions
        'wtfplv2': upt.licenses.WTFPLicense,
        'eiffelforumlicense,version2':
            upt.licenses.EiffelForumLicenseTwoDotZero,
        # other
        'gnuafferogeneralpubliclicensev3.0':
            upt.licenses.GNUAfferoGeneralPublicLicenseThreeDotZero,
        # bsdstyle
        # psflicense  # Missing version
        # gnu3  # GPL, LGPL?
        'gnulgplv2.1': upt.licenses.GNULesserGeneralPublicLicenseTwoDotOnePlus,
        # seefilelicense
        'licensegpl2': upt.licenses.GNUGeneralPublicLicenseTwo,
        'agpl3.0+': upt.licenses.GNUAfferoGeneralPublicLicenseThreeDotZeroPlus,
        'bsd(2clause)': upt.licenses.BSDTwoClauseLicense,
        'gpl3oranylaterversion': upt.licenses.GNUGeneralPublicLicenseThreePlus,
        'freebsdlicense': upt.licenses.BSDTwoClauseLicense,
        'https://opensource.org/licenses/mit': upt.licenses.MITLicense,
        # python(mitstyle)
        'ccbysa4.0license': upt.licenses.CCBYSAFourDotZero,
        'glpv3': upt.licenses.GNUGeneralPublicLicenseThree,
        'apachelicense,2.0': upt.licenses.ApacheLicenseTwoDotZero,
        'lgplv3license':
            upt.licenses.GNULesserGeneralPublicLicenseThreeDotZero,
        # proprietaryhttps://aka.ms/azuremlpreviewsdklicense
        '3bsd': upt.licenses.BSDThreeClauseLicense,
        # cc  # Missing version
        'asl2': upt.licenses.ApacheLicenseTwoDotZero,
        'ccbysa4.0': upt.licenses.CCBYSAFourDotZero,
        # lgpllicense  # Missing version
        # mitstyle
        # mpl1.1/gpl2.0/lgpl2.1
        'gnugeneralpubliclicense(gpl)v3':
            upt.licenses.GNUGeneralPublicLicenseThree,
        '(new)bsd': upt.licenses.BSDThreeClauseLicense,
        # mitorpsf
        # mit/expat
        # eclipsepubliclicense
        # na
        # lgpl,seealsolicense.txt
        '[\'mit\']': upt.licenses.MITLicense,
        # x11
        'aslv2': upt.licenses.ApacheLicenseTwoDotZero,
        'lgpl2': upt.licenses.GNULesserGeneralPublicLicenseTwoDotZero,
        # apachesoftware
        'lgplversion3orlater':
            upt.licenses.GNULesserGeneralPublicLicenseThreeDotZeroPlus,
        'afferogplv3':
            upt.licenses.GNUAfferoGeneralPublicLicenseThreeDotZero,
        # generalpubliclicence  # Missing version
        # osiapproved
        'gnugeneralpubliclicense3': upt.licenses.GNUGeneralPublicLicenseThree,
        'gplv.3': upt.licenses.GNUGeneralPublicLicenseThree,
        'ccbyncsa4.0': upt.licenses.CCBYSAFourDotZero,
        # 'seelicensefile'
        # artisticlicense  # Missing version
        'gpl2.0+': upt.licenses.GNUGeneralPublicLicenseTwoPlus,
        'zlib/libpng': upt.licenses.ZlibLibpngLicense,
        'generalpubliclicence2': upt.licenses.GNUGeneralPublicLicenseTwo,
        # epl  # Missing version
        'gnugeneralpubliclicensev3orlater':
            upt.licenses.GNUGeneralPublicLicenseThreePlus,
        'zlib/libpnglicense': upt.licenses.ZlibLibpngLicense,
        'apacheversion2': upt.licenses.ApacheLicenseTwoDotZero,
        'lgpl(version3orlater)':
            upt.licenses.GNULesserGeneralPublicLicenseThreeDotZeroPlus,
        # 9dwlab
        'gnuafferogplv3':
            upt.licenses.GNUAfferoGeneralPublicLicenseThreeDotZero,
        # ics
        'apachesoftwarelicenseversion2.0':
            upt.licenses.ApacheLicenseTwoDotZero,
        # bsdstyle,seelicense.txtfordetails
        'osiapproved::mitlicense': upt.licenses.MITLicense,
        # nolicense
        'eupl1.1': upt.licenses.EuropeanUnionPublicLicenseOneDotOne,
        # copyright(c)2014awebercommunicationsallrightsreserved.redistributionanduseinsourceandbinaryforms,withorwithoutmodificati
        'newstylebsd': upt.licenses.BSDThreeClauseLicense,
        'gnugpl2.0': upt.licenses.GNUGeneralPublicLicenseTwo,
        # osiapproved::bsdlicense
        'gnu3.0': upt.licenses.GNUGeneralPublicLicenseThree,
        'ccby4.0': upt.licenses.CCBYSAFourDotZero,
        # copyright©2014–baptistefontainepermissionisherebygranted,freeofcharge,toanypersonobtainingacopyofthissoftwareandassociat
        'ccbync4.0': upt.licenses.CCBYSAFourDotZero,
        # http://www.opensource.org/licenses/bsdlicense.php
        # silofl1.1
        # artistic
        # agpl3,eupl1.2
        # license::cc01.0universal(cc01.0)publicdomaindedication
        'apachelicencev2.0': upt.licenses.ApacheLicenseTwoDotZero,
        # affero  # Missing version
        'boost': upt.licenses.BoostSoftwareLicense,

    }

    try:
        return [pypi_stats[license_field]()]
    except KeyError:
        return []


def guess_licenses_from_sdist(archive_url):
    # TODO: we might want to use a wrapper around tarfile, zipfile and
    # other archive-related Python modules, rather than using this hack.
    if (archive_url.endswith('.tar.gz') or
            archive_url.endswith('.tgz') or
            archive_url.endswith('.tar.bz2')):
        open_archive = tarfile.open
        get_names = getattr(tarfile.TarFile, 'getnames')
    elif archive_url.endswith('.zip'):
        open_archive = zipfile.ZipFile
        get_names = getattr(zipfile.ZipFile, 'namelist')
    else:
        raise ValueError(f'Unknown sdist archive type at {archive_url}')

    licenses = []
    with tempfile.NamedTemporaryFile() as archive:
        urlretrieve(archive_url, archive.name)
        ar = open_archive(archive.name)
        license_files = [name for name in get_names(ar)
                         if name.endswith('/LICENSE')
                         or name.endswith('/LICENSE.txt')]
        if not license_files:
            return []

        with tempfile.TemporaryDirectory() as d:
            for license_file in license_files:
                ar.extract(license_file, path=d)
                path = f'{d}/{license_file}'
                licenses.append(upt.licenses.guess_from_file(path))
    return licenses


def guess_licenses(json_data, sdist_url):
    # First, we will try to use the classifiers to guess the right license(s).
    classifiers = json_data['info'].get('classifiers', [])
    licenses = guess_licenses_using_classifiers(classifiers)

    # Mutliple possible outcomes:
    # - We found only one license, and could identify it: we're done.
    # - We found more than one license: let's return everything. Even if some
    #   of the found licenses are not properly identified, we're in a "complex"
    #   case and it is probably best for a human to check what licenses apply.
    if licenses and (len(licenses) > 1 or
                     not isinstance(licenses[0], DEFAULT_LICENSE)):
        return licenses

    # ... or we get here for one of two reasons:
    # - We found nothing using the classifiers
    # - We found only one license, but could not identify it
    license_field = json_data['info'].get('license', '') or ''
    licenses = guess_licenses_using_license_field(license_field)
    if licenses and (len(licenses) > 1 or
                     not isinstance(licenses[0], DEFAULT_LICENSE)):
        return licenses

    # Still no luck! Let us try to read the LICENSE from the source package.
    if sdist_url:
        try:
            return guess_licenses_from_sdist(sdist_url)
        except ValueError:
            return []

    # We did our best, and it was not enough.
    return []
