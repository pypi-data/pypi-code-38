# Copyright (C) 2016 Red Hat
#
# This file is part of fedfind.
#
# fedfind is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Adam Williamson <awilliam@redhat.com>

# these are all kinda inappropriate for pytest patterns
# pylint: disable=old-style-class, no-init, protected-access, no-self-use, unused-argument
# pylint: disable=too-many-public-methods

"""Tests for helpers.py."""

from __future__ import unicode_literals
from __future__ import print_function

import codecs
import datetime
import hashlib
import os
import shutil

import mock
import pytest
# pylint: disable=import-error
from six.moves.urllib.request import Request

import fedfind.const
import fedfind.helpers

URL = 'https://dl.fedoraproject.org'
PDC_JSON = {
    "results": ['some', 'results'],
    "next": False
}
PDC_JSON_REAL = {
    "results": [
        {
            'compose_id': 'Fedora-24-20160314.1',
            'compose_label': 'Alpha-1.1'
        }
    ],
    "next": False
}

SERVDVD_DICT = {
    "arch": "i386",
    "bootable": True,
    "checksums": {
        "sha256": "2b50438d2b96a72fac765490601d8cd24bae6ac26fa68f423b70cdb2b3bd43b3"
    },
    "disc_count": 1,
    "disc_number": 1,
    "format": "iso",
    "implant_md5": "6fae584ebfc6d462b44d2091c5425cb4",
    "mtime": 1475645667,
    "path": "Server/i386/iso/Fedora-Server-dvd-i386-25_Beta-1.1.iso",
    "size": 2108686336,
    "subvariant": "Server",
    "type": "dvd",
    "volume_id": "Fedora-S-dvd-i386-25"
}

WORKATOMIC_DICT = {
    "arch": "x86_64",
    "bootable": True,
    "checksums": {
        "sha256": "ca2aaa84009b55798eb62ab68f5d109a139f0471443e93fb600b1768555435b3"
    },
    "disc_count": 1,
    "disc_number": 1,
    "format": "iso",
    "implant_md5": "942e5efbada935b7376a63aeece53123",
    "mtime": 1475647664,
    "path": "Workstation/x86_64/iso/Fedora-Workstation-dvd-x86_64-25_Beta-1.1.iso",
    "size": 2345664512,
    "subvariant": "Workstation",
    "type": "boot",
    "volume_id": "Fedora-25-x86_64"
}

CLOUDRAWXZ_DICT = {
    "arch": "x86_64",
    "bootable": False,
    "checksums": {
        "sha256": "19e6503e29e82bea1f5a41c6a0bd773dac7a3e38507a6edc0aea3b3cf2359d18"
    },
    "disc_count": 1,
    "disc_number": 1,
    "format": "raw.xz",
    "implant_md5": "",
    "mtime": 1475647224,
    "path": "CloudImages/x86_64/images/Fedora-Cloud-Base-25_Beta-1.1.x86_64.raw.xz",
    "size": 237423412,
    "subvariant": "Cloud_Base",
    "type": "raw-xz",
    "volume_id": ""
}


@pytest.mark.usefixtures("clean_home")
class TestHelpers:
    """Tests for the functions in helpers.py."""
    def test_date_check(self):
        """Tests for date_check."""
        invalid = 'notadate'
        # this looks a bit silly, but we want the values of 'valid'
        # and 'obj' to match
        now = datetime.datetime.now()
        valid = now.strftime('%Y%m%d')
        obj = datetime.datetime.strptime(valid, '%Y%m%d')

        # Default case: checking valid obj or str should return obj
        assert fedfind.helpers.date_check(obj, out='obj') == obj
        assert fedfind.helpers.date_check(valid, out='obj') == obj
        assert fedfind.helpers.date_check(obj) == obj
        assert fedfind.helpers.date_check(valid) == obj

        # Checking valid obj or str with out='str' should return str
        assert fedfind.helpers.date_check(obj, out='str') == valid
        assert fedfind.helpers.date_check(valid, out='str') == valid

        # Checking valid with out='both' should return a tuple of both
        assert fedfind.helpers.date_check(obj, out='both') == (valid, obj)
        assert fedfind.helpers.date_check(valid, out='both') == (valid, obj)

        # Checking invalid with fail_raise=False should return False
        assert fedfind.helpers.date_check(invalid, fail_raise=False) is False

        # Checking invalid with fail_raise=True or default should
        # raise ValueError
        with pytest.raises(ValueError):
            fedfind.helpers.date_check(invalid, fail_raise=True)
        with pytest.raises(ValueError):
            fedfind.helpers.date_check(invalid)

    @mock.patch('fedfind.helpers.urlopen', return_value=True, autospec=True)
    def test_urlopen_retries_good(self, fakeopen):
        """Test urlopen_retries works and only calls urlopen once in
        normal success case.
        """
        assert fedfind.helpers.urlopen_retries(URL) is True
        fakeopen.assert_called_with(URL)
        assert fakeopen.call_count == 1

    @mock.patch('fedfind.helpers.urlopen', side_effect=ValueError, autospec=True)
    def test_urlopen_retries_bad(self, fakeopen):
        """Test urlopen_retries tries 5 times then raises ValueError
        if urlopen isn't working.
        """
        with pytest.raises(ValueError):
            fedfind.helpers.urlopen_retries(URL)
        fakeopen.assert_called_with(URL)
        assert fakeopen.call_count == 5

    @mock.patch('fedfind.helpers.urlopen', autospec=True)
    def test_download_json(self, fakeopen):
        """Test download_json decodes and returns the json provided by
        urlopen.
        """
        # this is the MagicMock that calling fakeopen returns
        fakefh = fakeopen.return_value
        # let's make it look like some JSON...
        fakefh.read.return_value = b'{"foo": "bar"}'
        assert fedfind.helpers.download_json(URL) == {'foo': 'bar'}

    @mock.patch('fedfind.helpers.urlopen', autospec=True)
    def test_url_exists_http_good(self, fakeopen):
        """Test url_exists is True when urlopen returns without error."""
        assert fedfind.helpers.url_exists(URL) is True
        fakeopen.assert_called_with(URL)

    @mock.patch('fedfind.helpers.urlopen', side_effect=ValueError('foo'), autospec=True)
    def test_url_exists_http_bad(self, fakeopen):
        """Test url_exists is False when urlopen raises error."""
        assert fedfind.helpers.url_exists(URL) is False

    def test_url_exists_invalid(self):
        """Test url_exists raises an error when the URL is garbage."""
        with pytest.raises(ValueError):
            fedfind.helpers.url_exists('jfohpjsph#^3#@^#')

    @mock.patch('fedfind.helpers.urlopen_retries', autospec=True)
    def test_get_size(self, fakeopen):
        """Test get_size works as expected, if it gets the expected
        response from urlopen_retries.
        """
        fakeresp = fakeopen.return_value
        fakeresp.info.return_value = {'Content-Length': 100}
        assert fedfind.helpers.get_size(URL) == 100

    def test_comma_list(self):
        """It splits lists on commas. It ain't rocket science."""
        assert fedfind.helpers.comma_list('foo,Bar,moo') == ['foo', 'bar', 'moo']

    def test_get_collections(self, json_collections):
        """Test _get_collections works correctly and caches."""
        (mocked, fakedata) = json_collections
        # download twice to check caching is working
        colls = fedfind.helpers._get_collections()
        colls = fedfind.helpers._get_collections()
        assert colls == fakedata
        assert mocked.call_count == 1

    def test_get_current_release(self, collections):
        """Test get_current_release gives expected values, with our
        fake collections data.
        """
        assert fedfind.helpers.get_current_release() == 23
        assert fedfind.helpers.get_current_release(branched=True) == 24

    def test_get_current_stables(self, collections):
        """Test get_current_stables gives the expected values."""
        assert fedfind.helpers.get_current_stables() == [22, 23]

    @pytest.mark.parametrize(
        ("path", "arch", "form", "typ", "subvariant", "disc_number"),
        # the image path to synthesize a dict for, and the expected values
        [
            # old-style two-week atomic compose
            ('Cloud_Atomic/x86_64/iso/Fedora-Cloud_Atomic-x86_64-23-20160313.iso',
             'x86_64', 'iso', 'dvd-ostree', 'Atomic', 1),
            ('Docker/x86_64/Fedora-Docker-Base-23-20160313.x86_64.tar.xz',
             'x86_64', 'tar.xz', 'docker', 'Docker_Base', 1),
            ('Cloud-Images/i386/Images/Fedora-Cloud-Base-23-20160313.i386.qcow2',
             'i386', 'qcow2', 'qcow2', 'Cloud_Base', 1),
            # Fedora Core 1 split discs
            ('i386/iso/yarrow-i386-disc1.iso', 'i386', 'iso', 'cd', 'Everything', 1),
            ('i386/iso/yarrow-i386-disc2.iso', 'i386', 'iso', 'cd', 'Everything', 2),
            # Various ostree cases
            # 25 Beta Workstation ostree installer
            ('Workstation/x86_64/iso/Fedora-Workstation-dvd-x86_64-25_Beta-1.1.iso',
             'x86_64', 'iso', 'dvd-ostree', 'Workstation', 1),
            # 24 two-week Atomic 20161008.0
            ('Atomic/x86_64/iso/Fedora-Atomic-dvd-x86_64-24-20161008.0.iso',
             'x86_64', 'iso', 'dvd-ostree', 'Atomic', 1),
            # F23 Final Atomic host
            ('Cloud_Atomic/x86_64/iso/Fedora-Cloud_Atomic-x86_64-23.iso',
             'x86_64', 'iso', 'dvd-ostree', 'Atomic', 1),
            # Nightly after pungi filename changes: Atomic host
            ('Atomic/x86_64/iso/Fedora-Atomic-ostree-x86_64-Rawhide-20161010.n.0.iso',
             'x86_64', 'iso', 'dvd-ostree', 'Atomic', 1),
            # Nightly after pungi filename changes: Atomic workstation
            ('Workstation/x86_64/iso/Fedora-Workstation-ostree-x86_64-Rawhide-20161010.n.0.iso',
             'x86_64', 'iso', 'dvd-ostree', 'Workstation', 1),
            # 'multi' image cases
            ('Multi/Fedora-15-Multi-Desktop.iso', '', 'iso', 'multi-desktop', 'Multi', 1),
            ('Multi/Fedora-15-Multi-Install.iso', '', 'iso', 'multi-install', 'Multi', 1),
        ]
    )
    def test_create_image_dict(self, path, arch, form, typ, subvariant, disc_number):
        """Check create_image_dict produces correct dicts with various
        standard and tricky cases.
        """
        # pylint: disable=too-many-arguments
        ret = fedfind.helpers.create_image_dict(path)
        assert ret == {
            'path': path,
            'arch': arch,
            'format': form,
            'type': typ,
            'subvariant': subvariant,
            'disc_number': disc_number
        }

    @mock.patch('fedfind.helpers.download_json', return_value=PDC_JSON, autospec=True)
    def test_pdc_query(self, fakejson):
        """Check pdc_query works correctly, with the canned PDC_JSON
        data.
        """
        assert fedfind.helpers.pdc_query('composes') == ['some', 'results']
        # first (and only) positional arg to the download_json call should be a Request
        req = fakejson.call_args[0][0]
        assert isinstance(req, Request)

    def test_find_cid(self):
        """Check find_cid works correctly, with various common and
        tricky cases.
        """
        res = fedfind.helpers.find_cid('https://foo.com/compose/Fedora-24-20160314.n.0/compose')
        assert res == 'Fedora-24-20160314.n.0'
        res = fedfind.helpers.find_cid('https://foo.com/compose/Fedora-24-20160314.0/compose')
        assert res == 'Fedora-24-20160314.0'
        res = fedfind.helpers.find_cid('https://foo.com/compose/Fedora-24-20160314.t.0/compose')
        assert res == 'Fedora-24-20160314.t.0'
        res = fedfind.helpers.find_cid(
            'https://foo.com/compose/Fedora-Rawhide-20160314.n.1/compose')
        assert res == 'Fedora-Rawhide-20160314.n.1'
        res = fedfind.helpers.find_cid(
            'https://foo.com/compose/twoweek/Fedora-Atomic-24-20161004.1/compose')
        assert res == 'Fedora-Atomic-24-20161004.1'
        res = fedfind.helpers.find_cid('FedoraRespin-24-20161206.0')
        assert res == 'FedoraRespin-24-20161206.0'
        res = fedfind.helpers.find_cid('FedoraRespin-24-updates-20161206.0')
        assert res == 'FedoraRespin-24-updates-20161206.0'
        # a few 'close but no cigars' just for safety...
        res = fedfind.helpers.find_cid('https://foo.com/compose/Fedora-24-20160314.t.u/compose')
        assert res == ''
        res = fedfind.helpers.find_cid('https://foo.com/compose/Fedora-24-20160314/compose')
        assert res == ''
        res = fedfind.helpers.find_cid('https://foo.com/compose/Fedora/24-20160314.n.0/compose')
        assert res == ''

    @pytest.mark.parametrize(
        ("cid", "short", "version", "version_type", "base_short", "base_version", "base_type",
         "variant", "date", "compose_type", "respin"),
        [
            ('Fedora-24-20160314.n.0', 'Fedora', '24', 'ga', '', '', '', '', '20160314', 'nightly',
             0),
            ('Fedora-24-20160314.0', 'Fedora', '24', 'ga', '', '', '', '', '20160314',
             'production', 0),
            ('Fedora-24-20160314.t.0', 'Fedora', '24', 'ga', '', '', '', '', '20160314', 'test', 0),
            ('Fedora-Rawhide-20160314.n.1', 'Fedora', 'Rawhide', 'ga', '', '', '', '', '20160314',
             'nightly', 1),
            ('Fedora-Atomic-24-20160628.0', 'Fedora-Atomic', '24', 'ga', '', '', '', '',
             '20160628', 'production', 0),
            ('Fedora-20-19700101.0', 'Fedora', '20', 'ga', '', '', '', '', '19700101',
             'production', 0),
            ('FedoraRespin-24-updates-20161206.0', 'FedoraRespin', '24', 'updates', '', '', '', '',
             '20161206', 'production', 0),
            # older fake Respin CID
            ('FedoraRespin-24-20161206.0', 'FedoraRespin', '24', 'ga', '', '', '', '', '20161206',
             'production', 0),
            # taken from productmd test_composeinfo
            ('Fedora-22-20160622.0', 'Fedora', '22', 'ga', '', '', '', '', '20160622', 'production',
             0),
            # FIXME: 'ci' is a valid compose type now but get_date_type_respin doesn't handle it
            # 'Fedora-22-20160622.ci.0'
            ('Fedora-22-updates-20160622.0', 'Fedora', '22', 'updates', '', '', '', '', '20160622',
             'production', 0),
            ('Fedora-22-updates-20160622.n.0', 'Fedora', '22', 'updates', '', '', '', '',
             '20160622', 'nightly', 0),
            ('Fedora-22-BASE-3-20160622.0', 'Fedora', '22', 'ga', 'BASE', '3', 'ga', '', '20160622',
             'production', 0),
            ('Fedora-22-BASE-3-20160622.n.0', 'Fedora', '22', 'ga', 'BASE', '3', 'ga', '',
             '20160622', 'nightly', 0),
            ('Fedora-22-updates-BASE-3-20160622.0', 'Fedora', '22', 'updates', 'BASE', '3', 'ga',
             '', '20160622', 'production', 0),
            ('Fedora-22-updates-BASE-3-20160622.n.0', 'Fedora', '22', 'updates', 'BASE', '3', 'ga',
             '', '20160622', 'nightly', 0),
            ('Fedora-22-BASE-3-updates-20160622.0', 'Fedora', '22', 'ga', 'BASE', '3', 'updates',
             '', '20160622', 'production', 0),
            ('Fedora-22-BASE-3-updates-20160622.n.0', 'Fedora', '22', 'ga', 'BASE', '3', 'updates',
             '', '20160622', 'nightly', 0),
            ('Fedora-22-updates-BASE-3-updates-20160622.0', 'Fedora', '22', 'updates', 'BASE', '3',
             'updates', '', '20160622', 'production', 0),
            ('Fedora-22-updates-BASE-3-updates-20160622.n.0', 'Fedora', '22', 'updates', 'BASE',
             '3', 'updates', '', '20160622', 'nightly', 0),
            ('Fedora-22-updates-BASE-3-updates-testing-20160622.n.0', 'Fedora', '22',
             'updates', 'BASE', '3', 'updates-testing', '', '20160622', 'nightly', 0),
            ('Fedora-22-updates-testing-BASE-3-updates-20160622.n.0', 'Fedora', '22',
             'updates-testing', 'BASE', '3', 'updates', '', '20160622', 'nightly', 0),
            ('Fedora-22-updates-testing-BASE-3-updates-testing-20160622.n.0', 'Fedora', '22',
             'updates-testing', 'BASE', '3', 'updates-testing', '', '20160622', 'nightly', 0),
            # Rawhide complex
            ('Fedora-Rawhide-updates-RHEL-6.3.4-20160513.t.1', 'Fedora', 'Rawhide', 'updates',
             'RHEL', '6.3.4', 'ga', '', '20160513', 'test', 1),
            # I think this is how a RHEL 5 one looks?
            ('Fedora-5-updates-Server-20160523.2', 'Fedora', '5', 'updates', '', '', '', 'Server',
             '20160523', 'production', 2),
            ('Fedora-5-updates-Client-20160523.2', 'Fedora', '5', 'updates', '', '', '', 'Client',
             '20160523', 'production', 2),
        ]
    )
    def test_parse_cid(self, cid, short, version, version_type, base_short, base_version,
                       base_type, variant, date, compose_type, respin):
        """Check parse_cid works correctly, with various known compose
        ID forms.
        """
        # pylint: disable=too-many-arguments
        assert fedfind.helpers.parse_cid(cid, dic=True) == {
            'short': short,
            'version': version,
            'version_type': version_type,
            'base_short': base_short,
            'base_version': base_version,
            'base_type': base_type,
            'variant': variant,
            'date': date,
            'compose_type': compose_type,
            'respin': respin
        }

    def test_parse_cid_tuple(self):
        """Check the two older tuple formats for parse_cid work as
        expected.
        """
        res = fedfind.helpers.parse_cid('Fedora-24-20160314.n.0')
        assert res == ('24', '20160314', 'nightly', 0)
        res = fedfind.helpers.parse_cid('Fedora-24-20160314.n.0', dist=True)
        assert res == ('Fedora', '24', '20160314', 'nightly', 0)
        res = fedfind.helpers.parse_cid('Fedora-Atomic-24-20160628.0', dist=True)
        assert res == ('Fedora-Atomic', '24', '20160628', 'production', 0)

    def test_parse_cid_error(self):
        """Check parse_cid raises ValueError for non-Pungi 4-ish CID."""
        with pytest.raises(ValueError):
            fedfind.helpers.parse_cid('23-20160530')

    @mock.patch('fedfind.helpers.download_json', return_value=PDC_JSON_REAL, autospec=True)
    def test_cid_from_label(self, fakejson):
        """Check cid_from_label works, using some real canned PDC
        data.
        """
        assert fedfind.helpers.cid_from_label('24', 'Alpha-1.1') == 'Fedora-24-20160314.1'

    @mock.patch('fedfind.helpers.download_json', return_value=PDC_JSON_REAL, autospec=True)
    def test_label_from_cid(self, fakejson):
        """Check label_from_cid works, using some real canned PDC
        data.
        """
        assert fedfind.helpers.label_from_cid('Fedora-24-20160314.1') == 'Alpha-1.1'

    def test_correct_image(self):
        """Test the correct_image function does all the corrections
        it ought to.
        """
        # dict with no 'issues' should generate identical result
        assert fedfind.helpers.correct_image(SERVDVD_DICT) == SERVDVD_DICT
        # Atomic installer dict should be modified as expected
        newdic = fedfind.helpers.correct_image(WORKATOMIC_DICT)
        # type should be changed
        assert newdic['type'] == 'dvd-ostree'
        # otherwise dict should be the same
        newdic['type'] = 'boot'
        assert newdic == WORKATOMIC_DICT

    def test_identify_image(self):
        """Test that identify_image provides the correct tuples with
        various image dicts, and respects its options correctly.
        """
        ident = fedfind.helpers.identify_image
        assert ident(SERVDVD_DICT) == ('Server', 'dvd', 'iso')
        assert ident(WORKATOMIC_DICT) == ('Workstation', 'dvd-ostree', 'iso')
        # test options
        assert ident(SERVDVD_DICT, out='tuple') == ('Server', 'dvd', 'iso')
        assert ident(SERVDVD_DICT, out='string') == ('Server-dvd-iso')
        assert ident(SERVDVD_DICT, lower=True) == ('server', 'dvd', 'iso')
        assert ident(CLOUDRAWXZ_DICT, undersub=False) == ('Cloud_Base', 'raw-xz', 'raw.xz')
        assert ident(CLOUDRAWXZ_DICT, undersub=True) == ('Cloud_Base', 'raw_xz', 'raw.xz')

    @pytest.mark.parametrize("flist", ('fedora', 'alt', 'archive'))
    def test_get_filelist(self, flist, http, clean_home):
        """Test _get_filelist with each of the filelists, in various
        ways (caching, failed downloads, etc.)
        """
        def check_file(flist, touch=False):
            """Inner function for doing the check (run multiple times)"""
            origfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'http',
                                    'pub', flist, 'imagelist-{0}'.format(flist))
            if touch:
                os.utime(origfile, None)
            gotcksum = hashlib.md5()
            origcksum = hashlib.md5()
            record = {}
            with fedfind.helpers._get_filelist(flist=flist, record=record) as testfh:
                assert testfh.name == os.path.join(clean_home, '.cache', 'fedfind',
                                                   'imagelist-{0}'.format(flist))
                for line in testfh:
                    gotcksum.update(line.encode('utf-8'))
            with codecs.open(origfile, encoding='utf-8') as origfh:
                for line in origfh:
                    origcksum.update(line.encode('utf-8'))
            assert gotcksum.digest() == origcksum.digest()
            return record

        check_file(flist)
        record = check_file(flist)
        assert record['cache'] is True

        record = check_file(flist, touch=True)
        assert record['cache'] is False

        # now make the download fail: we should still work using the
        # cached copy, but warn about it
        origconst = fedfind.const.HTTPS_DL
        fedfind.const.HTTPS_DL = 'http://localhost:5001/nonexistent'
        check_file(flist)
        # Reset the constant
        fedfind.const.HTTPS_DL = origconst

    @mock.patch('fedfind.helpers.download_json', return_value=PDC_JSON, autospec=True)
    def test_cachedir_vanish(self, http, clean_home):
        """Test that we recover from the cache dir suddenly vanishing.
        I saw this happen on openqa01 once - I think when we're using
        a temp dir as the cache location, it can get cleaned up by
        systemd or so while we're running.
        """
        fedfind.helpers._get_filelist(flist='fedora')
        assert os.path.exists(os.path.join(clean_home, '.cache', 'fedfind'))
        shutil.rmtree(os.path.join(clean_home, '.cache', 'fedfind'))
        fedfind.helpers._get_filelist(flist='fedora')
        assert os.path.exists(os.path.join(clean_home, '.cache', 'fedfind'))
        # also test pdc_query
        shutil.rmtree(os.path.join(clean_home, '.cache', 'fedfind'))
        # pass compose_id otherwise the function won't cache
        fedfind.helpers.pdc_query('composes', {'compose_id': 'Fedora-26-20170418.n.0'})
        assert os.path.exists(os.path.join(clean_home, '.cache', 'fedfind'))

# vim: set textwidth=100 ts=8 et sw=4:
