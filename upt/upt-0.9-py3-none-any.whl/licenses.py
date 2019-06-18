# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.

# Data about licenses come from:
# - https://opensource.org/licenses/alphabetical
# - https://opensource.org/licenses/category
# - https://www.gnu.org/licenses/license-list.en.html#GPLCompatibleLicenses
# - https://wiki.debian.org/DFSGLicenses
# - https://spdx.org/licenses/
import spdx_lookup


class License(object):
    def is_osi_approved(self):
        return False

    def is_gpl_compatible(self):
        return False

    def is_dfsg_compatible(self):
        return False

    def __eq__(self, other):
        return self.spdx_identifier == other.spdx_identifier


class OSIApprovedLicense(License):
    def is_osi_approved(self):
        return True


class GPLCompatibleLicense(License):
    def is_gpl_compatible(self):
        return True


class DFSGCompatibleLicense(License):
    def is_dfsg_compatible(self):
        return True


class UnknownLicense(License):
    """License returned when upt cannot guess the right license."""
    name = 'Unknown license - upt could not determine what it was'
    spdx_identifier = 'unknown'


class AcademicFreeLicenseOneDotOne(OSIApprovedLicense):
    name = 'Academic Free License 1.1'
    spdx_identifier = 'AFL-1.1'


class AcademicFreeLicenseOneDotTwo(OSIApprovedLicense):
    name = 'Academic Free License 1.2'
    spdx_identifier = 'AFL-1.2'


class AcademicFreeLicenseTwoDotZero(OSIApprovedLicense):
    name = 'Academic Free License 2.0'
    spdx_identifier = 'AFL-2.0'


class AcademicFreeLicenseTwoDotOne(OSIApprovedLicense):
    name = 'Academic Free License 2.1'
    spdx_identifier = 'AFL-2.1'


class AcademicFreeLicenseThreeDotZero(OSIApprovedLicense):
    name = 'Academic Free License 3.0'
    spdx_identifier = 'AFL-3.0'


class AdaptivePublicLicense(OSIApprovedLicense):
    name = 'Adaptive Public License'
    spdx_identifier = 'APL-1.0'


class AladdinFreePublicLicense(License):
    name = 'Aladdin Free Public License'
    spdx_identifier = 'Aladdin'


class ApacheLicenseOneDotZero(OSIApprovedLicense):
    name = 'Apache License 1.0'
    spdx_identifier = 'Apache-1.0'


class ApacheLicenseOneDotOne(OSIApprovedLicense):
    name = 'Apache License 1.1'
    spdx_identifier = 'Apache-1.1'


class ApacheLicenseTwoDotZero(OSIApprovedLicense, GPLCompatibleLicense):
    name = 'Apache License 2.0'
    spdx_identifier = 'Apache-2.0'


class ApplePublicSourceLicenseOneDotZero(OSIApprovedLicense):
    name = 'Apple Public Source License 1.0'
    spdx_identifier = 'APSL-1.0'


class ApplePublicSourceLicenseOneDotOne(OSIApprovedLicense):
    name = 'Apple Public Source License 1.1'
    spdx_identifier = 'APSL-1.1'


class ApplePublicSourceLicenseOneDotTwo(OSIApprovedLicense):
    name = 'Apple Public Source License 1.2'
    spdx_identifier = 'APSL-1.2'


class ApplePublicSourceLicenseTwoDotTwo(OSIApprovedLicense):
    name = 'Apple Public Source License'
    spdx_identifier = 'APSL-2.0'


class ArtisticLicenseOneDotZero(DFSGCompatibleLicense,
                                OSIApprovedLicense):
    name = 'Artistic License 1.0'
    spdx_identifier = 'Artistic-1.0'


class ArtisticLicenseTwoDotZero(DFSGCompatibleLicense,
                                GPLCompatibleLicense,
                                OSIApprovedLicense):
    name = 'Artistic License 2.0'
    spdx_identifier = 'Artistic-2.0'


class AttributionAssuranceLicense(OSIApprovedLicense):
    name = 'Attribution Assurance License'
    spdx_identifier = 'AAL'


class BoostSoftwareLicense(OSIApprovedLicense, GPLCompatibleLicense):
    name = 'Boost Software License'
    spdx_identifier = 'BSL-1.0'


class BSDTwoClauseLicense(OSIApprovedLicense, GPLCompatibleLicense):
    name = '2-clause BSD License'
    spdx_identifier = 'BSD-2-Clause'


class BSDTwoClausePatent(DFSGCompatibleLicense,
                         OSIApprovedLicense):
    name = 'BSD+Patent'
    spdx_identifier = 'BSD-2-Clause-Patent'


class BSDThreeClauseLicense(OSIApprovedLicense, GPLCompatibleLicense):
    name = '3-clause BSD License'
    spdx_identifier = 'BSD-3-Clause'


class CC0LicenceOneDotZero(GPLCompatibleLicense):
    name = 'Creative Commons Zero v1.0 Universal'
    spdx_identifier = 'CC0-1.0'


class CCBYSAFourDotZero(DFSGCompatibleLicense, GPLCompatibleLicense):
    name = 'Creative Commons Attribution Share Alike 4.0 International'
    spdx_identifier = 'CC-BY-SA-4.0'


class CeCILLBLicense(License):
    name = 'CeCILL-B'
    spdx_identifier = 'CECILL-B'


class CeCILLCLicense(License):
    name = 'CeCILL-C'
    spdx_identifier = 'CECILL-C'


class CeCILLTwoDotZero(GPLCompatibleLicense):
    name = 'CeCILL License 2.0'
    spdx_identifier = 'CECILL-2.0'


class CeCILLTwoDotOne(OSIApprovedLicense, GPLCompatibleLicense):
    name = 'CeCILL License 2.1'
    spdx_identifier = 'CECILL-2.1'


class ClarifiedArtisticLicence(GPLCompatibleLicense):
    name = 'Clarified Artistic License'
    spdx_identifier = 'ClArtistic'


class CNRIPythonLicense(OSIApprovedLicense):
    name = 'CNRI Python License'
    spdx_identifier = 'CNRI-Python'


class CommonDevelopmentAndDistributionLicenseOneDotZero(OSIApprovedLicense):
    name = 'Common Development and Distribution License 1.0'
    spdx_identifier = 'CDDL-1.0'


class CommonPublicLicenseOneDotZero(DFSGCompatibleLicense,
                                    OSIApprovedLicense):
    name = 'Common Public License'
    spdx_identifier = 'CPL-1.0'


class CommonPublicAttributionLicenseOneDotZero(OSIApprovedLicense):
    name = 'Common Public Attribution License 1.0'
    spdx_identifier = 'CPAL-1.0'


class ComputerAssociatesTrustedOpenSourceLicenseOneDotOne(OSIApprovedLicense):
    name = 'Computer Associates Trusted Open Source License 1.1'
    spdx_identifier = 'CATOSL-1.1'


class CUAOfficePublicLicenseOneDotZero(OSIApprovedLicense):
    name = 'CUA Office Public License Version 1.0'
    spdx_identifier = 'CUA-OPL-1.0'


class EUDataGridSoftwareLicense(OSIApprovedLicense, GPLCompatibleLicense):
    name = 'EU DataGrid Software License'
    spdx_identifier = 'EUDatagrid'


class EclipsePublicLicenseOneDotZero(DFSGCompatibleLicense,
                                     OSIApprovedLicense):
    name = 'Eclipse Public License 1.0'
    spdx_identifier = 'EPL-1.0'


class EclipsePublicLicenseTwoDotZero(OSIApprovedLicense):
    name = 'Eclipse Public License 2.0'
    spdx_identifier = 'EPL-2.0'


class ECosLicenseTwoDotZero(OSIApprovedLicense, GPLCompatibleLicense):
    name = 'eCos License version 2.0'
    spdx_identifier = 'eCos-2.0'


class EducationalCommunityLicenseTwoDotZero(OSIApprovedLicense,
                                            GPLCompatibleLicense):
    name = 'Educational Community License, Version 2.0'
    spdx_identifier = 'ECL-2.0'


class EiffelForumLicenseTwoDotZero(OSIApprovedLicense, GPLCompatibleLicense):
    name = 'Eiffel Forum License V2.0'
    spdx_identifier = 'EFL-2.0'


class EntessaPublicLicense(OSIApprovedLicense):
    name = 'Entessa Public License'
    spdx_identifier = 'Entessa'


class EuropeanUnionPublicLicenseOneDotZero(License):
    name = 'European Union Public License, Version 1.0'
    spdx_identifier = 'EUPL-1.0'


class EuropeanUnionPublicLicenseOneDotOne(OSIApprovedLicense):
    name = 'European Union Public License, Version 1.1'
    spdx_identifier = 'EUPL-1.1'


class EuropeanUnionPublicLicenseOneDotTwo(OSIApprovedLicense):
    name = 'European Union Public License, Version 1.2'
    spdx_identifier = 'EUPL-1.2'


class FairLicense(OSIApprovedLicense):
    name = 'Fair License'
    spdx_identifier = 'Fair'


class FrameworxLicenseOneDotZero(OSIApprovedLicense):
    name = 'Frameworx Open License 1.0'
    spdx_identifier = 'Frameworx-1.0'


class FreePublicLicense(OSIApprovedLicense):
    name = 'Free Public License 1.0.0'
    spdx_identifier = '0BSD'


class GNUAfferoGeneralPublicLicenseThreeDotZero(DFSGCompatibleLicense,
                                                GPLCompatibleLicense,
                                                OSIApprovedLicense):
    name = 'GNU Affero General Public License version v3.0 only'
    spdx_identifier = 'AGPL-3.0-only'


class GNUAfferoGeneralPublicLicenseThreeDotZeroPlus(DFSGCompatibleLicense,
                                                    GPLCompatibleLicense,
                                                    OSIApprovedLicense):
    name = 'GNU Affero General Public License version v3.0 or later'
    spdx_identifier = 'AGPL-3.0-or-later'


class GNUFreeDocumentationLicenseOneDotOne(License):
    name = 'GNU Free Documentation License v1.1'
    spdx_identifier = 'GFDL-1.1'


class GNUFreeDocumentationLicenseOneDotTwo(License):
    name = 'GNU Free Documentation License v1.2'
    spdx_identifier = 'GFDL-1.2'


class GNUFreeDocumentationLicenseOneDotThree(License):
    name = 'GNU Free Documentation License v1.3'
    spdx_identifier = 'GFDL-1.3'


class GNUGeneralPublicLicenseTwo(DFSGCompatibleLicense,
                                 GPLCompatibleLicense,
                                 OSIApprovedLicense):
    name = 'GNU General Public License v2.0 only'
    spdx_identifier = 'GPL-2.0-only'


class GNUGeneralPublicLicenseTwoPlus(DFSGCompatibleLicense,
                                     GPLCompatibleLicense,
                                     OSIApprovedLicense):
    name = 'GNU General Public License version v2.0 or later'
    spdx_identifier = 'GPL-2.0-or-later'


class GNUGeneralPublicLicenseThree(DFSGCompatibleLicense,
                                   GPLCompatibleLicense,
                                   OSIApprovedLicense):
    name = 'GNU General Public License v3.0'
    spdx_identifier = 'GPL-3.0'


class GNUGeneralPublicLicenseThreePlus(DFSGCompatibleLicense,
                                       GPLCompatibleLicense,
                                       OSIApprovedLicense):
    name = 'GNU General Public License v3.0 or later'
    spdx_identifier = 'GPL-3.0-or-later'


class GNULesserGeneralPublicLicenseTwoDotZero(DFSGCompatibleLicense,
                                              GPLCompatibleLicense,
                                              OSIApprovedLicense):
    name = 'GNU Lesser General Public License v2 only'
    spdx_identifier = 'LGPL-2.0-only'


class GNULesserGeneralPublicLicenseTwoDotZeroPlus(DFSGCompatibleLicense,
                                                  GPLCompatibleLicense,
                                                  OSIApprovedLicense):
    name = 'GNU Lesser General Public License v2 or later'
    spdx_identifier = 'LGPL-2.0-or-later'


class GNULesserGeneralPublicLicenseTwoDotOne(DFSGCompatibleLicense,
                                             GPLCompatibleLicense,
                                             OSIApprovedLicense):
    name = 'GNU Lesser General Public License v2.1 only'
    spdx_identifier = 'LGPL-2.1-only'


class GNULesserGeneralPublicLicenseTwoDotOnePlus(DFSGCompatibleLicense,
                                                 GPLCompatibleLicense,
                                                 OSIApprovedLicense):
    name = 'GNU Lesser General Public License v2.1 or later'
    spdx_identifier = 'LGPL-2.1-or-later'


class GNULesserGeneralPublicLicenseThreeDotZero(DFSGCompatibleLicense,
                                                GPLCompatibleLicense,
                                                OSIApprovedLicense):
    name = 'GNU Lesser General Public License v3.0 only'
    spdx_identifier = 'LGPL-3.0-only'


class GNULesserGeneralPublicLicenseThreeDotZeroPlus(DFSGCompatibleLicense,
                                                    GPLCompatibleLicense,
                                                    OSIApprovedLicense):
    name = 'GNU Lesser General Public License v3.0 or later'
    spdx_identifier = 'LGPL-3.0-or-later'


class HistoricalPermissionNoticeAndDisclaimerLicense(OSIApprovedLicense,
                                                     GPLCompatibleLicense):
    name = 'Historical Permission Notice and Disclaimer'
    spdx_identifier = 'HPND'


class IBMPublicLicense(DFSGCompatibleLicense,
                       OSIApprovedLicense):
    name = 'IBM Public License 1.0'
    spdx_identifier = 'IPL-1.0'


class IntelOpenSourceLicense(OSIApprovedLicense, GPLCompatibleLicense):
    name = 'Intel Open Source License'
    spdx_identifier = 'Intel'


class IPAFontLicense(OSIApprovedLicense):
    name = 'IPA Font License'
    spdx_identifier = 'IPA'


class ISCLicense(DFSGCompatibleLicense,
                 GPLCompatibleLicense,
                 OSIApprovedLicense):
    name = 'ISC License'
    spdx_identifier = 'ISC'


class LaTeXProjectPublicLicenseOneDotThreeC(OSIApprovedLicense):
    name = 'LaTeX Project Public License 1.3c'
    spdx_identifier = 'LPPL-1.3c'


class LiLiQPLicenseOneDotOne(OSIApprovedLicense):
    name = 'Licence Libre du Québec – Permissive version 1.1'
    spdx_identifier = 'LiLiQ-P-1.1'


class LiLiQRLicenseOneDotOne(OSIApprovedLicense):
    name = 'Licence Libre du Québec – Réciprocité version 1.1'
    spdx_identifier = 'LiLiQ-R-version 1.'


class LiLiQRPlusLicenseOneDotOne(OSIApprovedLicense):
    name = 'Licence Libre du Québec – Réciprocité forte version 1.1'
    spdx_identifier = 'LiLiQ-Rplus-1.1'


class LucentPublicLicenseOneDotZeroTwo(OSIApprovedLicense):
    name = 'Lucent Public License Version 1.02'
    spdx_identifier = 'LPL-1.02'


class MirOSLicense(DFSGCompatibleLicense,
                   OSIApprovedLicense):
    name = 'MirOS Licence'
    spdx_identifier = 'MirOS'


class MicrosoftPublicLicense(OSIApprovedLicense):
    name = 'Microsoft Public License'
    spdx_identifier = 'MS-PL'


class MicrosoftReciprocalLicense(OSIApprovedLicense):
    name = 'Microsoft Reciprocal License'
    spdx_identifier = 'MS-RL'


class MITLicense(DFSGCompatibleLicense,
                 GPLCompatibleLicense,
                 OSIApprovedLicense):
    name = 'MIT License'
    spdx_identifier = 'MIT'


class MotosotoLicense(OSIApprovedLicense):
    name = 'Motosoto License'
    spdx_identifier = 'Motosoto'


class MozillaPublicLicenseOneDotZero(DFSGCompatibleLicense,
                                     OSIApprovedLicense):
    name = 'Mozilla Public License 1.0'
    spdx_identifier = 'MPL-1.0'


class MozillaPublicLicenseOneDotOne(DFSGCompatibleLicense,
                                    OSIApprovedLicense):
    name = 'Mozilla Public License 1.1'
    spdx_identifier = 'MPL-1.1'


class MozillaPublicLicenseTwoDotZero(DFSGCompatibleLicense,
                                     GPLCompatibleLicense,
                                     OSIApprovedLicense):
    name = 'Mozilla Public License 2.0'
    spdx_identifier = 'MPL-2.0'


class MulticsLicense(OSIApprovedLicense):
    name = 'Multics License'
    spdx_identifier = 'Multics'


class NASAOpenSourceArgreementOneDotThree(OSIApprovedLicense):
    name = 'NASA Open Source Agreement 1.3'
    spdx_identifier = 'NASA-1.3'


class NTPLicense(OSIApprovedLicense):
    name = 'NTP License'
    spdx_identifier = 'NTP'


class NaumenPublicLicense(OSIApprovedLicense):
    name = 'Naumen Public License'
    spdx_identifier = 'Naumen'


class NethackGeneralPublicLicense(OSIApprovedLicense):
    name = 'Nethack General Public License'
    spdx_identifier = 'NGPL'


class NetscapePublicLicenseOneDotZero(License):
    # See https://en.wikipedia.org/wiki/Netscape_Public_License
    name = 'Netscape Public License 1.0'
    spdx_identifier = 'NPL-1.0'


class NetscapePublicLicenseOneDotOne(License):
    # See https://en.wikipedia.org/wiki/Netscape_Public_License
    name = 'Netscape Public License 1.1'
    spdx_identifier = 'NPL-1.1'


class NokiaOpenSourceLicense(OSIApprovedLicense):
    name = 'Nokia Open Source License'
    spdx_identifier = 'Nokia'


class NonProfitOpenSoftwareLicenseThreeDotZero(OSIApprovedLicense):
    name = 'Non-Profit Open Software License 3.0'
    spdx_identifier = 'NPOSL-3.0'


class OCLCResearchPublicLicenseTwoDotZero(OSIApprovedLicense):
    name = 'OCLC Research Public License 2.0'
    spdx_identifier = 'OCLC-2.0'


class OpenGroupTestSuiteLicense(OSIApprovedLicense):
    name = 'Open Group Test Suite License'
    spdx_identifier = 'OGTSL'


class OpenSoftwareLicense(OSIApprovedLicense):
    name = 'Open Software License 3.0'
    spdx_identifier = 'OSL-3.0'


class OpenSSLLicense(DFSGCompatibleLicense):
    name = 'OpenSSL License'
    spdx_identifier = 'OpenSSL'


class OSETPublicLicenseVersionTwoDotOne(OSIApprovedLicense):
    name = 'OSET Public License version 2.1'
    spdx_identifier = 'OSET-PL-2.1'


class PerlLicense(DFSGCompatibleLicense,
                  GPLCompatibleLicense,
                  OSIApprovedLicense):
    name = 'Perl'
    spdx_identifier = 'Artistic-1.0-Perl'


class PHPLicenseThreeDotZero(OSIApprovedLicense):
    name = 'PHP License 3.0'
    spdx_identifier = 'PHP-3.0'


class PostgreSQLLicense(OSIApprovedLicense):
    name = 'The PostgreSQL License'
    spdx_identifier = 'PostgreSQL'


class PythonLicenseTwoDotZero(OSIApprovedLicense):
    name = 'Python License 2.0'
    spdx_identifier = 'Python-2.0'


class QPublicLicenseOneDotZero(OSIApprovedLicense):
    # Maybe DFSGCompatibleLicense (see https://wiki.debian.org/DFSGLicenses).
    name = 'Q Public License'
    spdx_identifier = 'QPL-1.0'


class RealNetworksPublicSourceLicenseVOneDotZero(OSIApprovedLicense):
    name = 'RealNetworks Public Source License V1.0'
    spdx_identifier = 'RPSL-1.0'


class ReciprocalPublicLicenseOneDotFive(OSIApprovedLicense):
    name = 'Reciprocal Public License 1.5'
    spdx_identifier = 'RPL-1.5'


class RicohSourceCodePublicLicense(OSIApprovedLicense):
    name = 'Ricoh Source Code Public License'
    spdx_identifier = 'RSCPL'


class RubyLicense(DFSGCompatibleLicense,
                  GPLCompatibleLicense):
    name = 'Ruby License'
    spdx_identifier = 'Ruby'


class SILOpenFrontLicenseOneDotOne(DFSGCompatibleLicense,
                                   OSIApprovedLicense):
    name = 'SIL Open Font License 1.1'
    spdx_identifier = 'OFL-1.1'


class SimplePublicLicenseTwoDotZero(OSIApprovedLicense):
    name = 'Simple Public License 2.0'
    spdx_identifier = 'SimPL-2.0'


class SleepycatLicense(OSIApprovedLicense, GPLCompatibleLicense):
    name = 'Sleepycat License'
    spdx_identifier = 'Sleepycat'


class SunIndustryStandardsSourceLicenceOneDotOne(OSIApprovedLicense):
    name = 'Sun Industry Standards Source License v1.1'
    spdx_identifier = 'SISSL'


class SunPublicLicense(OSIApprovedLicense):
    name = 'Sun Public License 1.0'
    spdx_identifier = 'SPL-1.0'


class SybaseOpenWatcomPublicLicense(OSIApprovedLicense):
    name = 'Sybase Open Watcom Public License 1.0'
    spdx_identifier = 'Watcom-1.0'


class NCSALicense(OSIApprovedLicense, GPLCompatibleLicense):
    name = 'University of Illinois/NCSA Open Source License'
    spdx_identifier = 'NCSA'


class UniversalPermissiveLicense(OSIApprovedLicense, GPLCompatibleLicense):
    name = 'Universal Permissive License'
    spdx_identifier = 'UPL'


class VovidaSoftwareLicenseVOneDotZero(OSIApprovedLicense):
    name = 'Vovida Software License v. 1.0'
    spdx_identifier = 'VSL-1.0'


class W3CLicense(OSIApprovedLicense, GPLCompatibleLicense):
    name = 'W3C License'
    spdx_identifier = 'W3C'


class WTFPLicense(DFSGCompatibleLicense, GPLCompatibleLicense):
    name = 'Do What The F*ck You Want To Public License'
    spdx_identifier = 'WTFPL'


class WxWindowsLibraryLicense(OSIApprovedLicense, GPLCompatibleLicense):
    name = 'wxWindows Library License'
    spdx_identifier = 'wxWindows'


class XNetLicense(OSIApprovedLicense):
    name = 'X.Net License'
    spdx_identifier = 'Xnet'


class ZopePublicLicenseTwoDotZero(OSIApprovedLicense, GPLCompatibleLicense):
    name = 'Zope Public License 2.0'
    spdx_identifier = 'ZPL-2.0'


class ZopePublicLicenseTwoDotOne(GPLCompatibleLicense):
    name = 'Zope Public License 2.1'
    spdx_identifier = 'ZPL-2.1'


class ZlibLicense(DFSGCompatibleLicense,
                  GPLCompatibleLicense,
                  OSIApprovedLicense):
    name = 'zlib License'
    spdx_identifier = 'zlib'


class ZlibLibpngLicense(DFSGCompatibleLicense,
                        GPLCompatibleLicense,
                        OSIApprovedLicense):
    name = 'zlib/libpng License with Acknowledgement'
    spdx_identifier = 'zlib-acknowledgement'


def get_license_by_spdx_identifier(spdx_id):
    """Return a License object corresponding to the given spdx id."""
    # Keys are spdx identifiers.
    # Values are License classes.
    spdx_ids_to_license = {}

    def get_all_subclasses(cls):
        for subclass in cls.__subclasses__():
            yield subclass
            yield from get_all_subclasses(subclass)

    for cls in set(get_all_subclasses(License)):
        try:
            spdx_ids_to_license[cls.spdx_identifier] = cls
        except AttributeError:  # No spdx_identifier on the base classes
            pass

    return spdx_ids_to_license.get(spdx_id, UnknownLicense)()


def guess_from_file(license_file, min_confidence=95):
    """Guess the licence using a license file.

    license_file: the path to a license file shipped by a project.
    min_confidence: on a scale of 0 to 100, the minimal confidence expected
                    when yielding a result. 0 will match almost anything, 100
                    will probably not match anything.

    Return an instance of a subclass of License if a license could be guessed,
    None otherwise.
    """
    if not 0 <= min_confidence <= 100:
        raise ValueError('min_confidence must be in [0; 100]')

    with open(license_file) as f:
        match = spdx_lookup.match(f.read())
        if match is None:
            return UnknownLicense()
        if match.confidence < min_confidence:
            return UnknownLicense()
        return get_license_by_spdx_identifier(match.license.id)
