#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
# (c) Copyright 2018 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
import json


def setup():
    from LbPlatformUtils.tests import utils
    utils.setup_all()


def teardown():
    from LbPlatformUtils.tests import utils
    utils.teardown_all()


# Content of https://lhcb-couchdb.cern.ch/nightlies-release/_design/names/_view/platforms?group=true
# as of 2018-02-05
BINARY_TAGS_DATA = '''{"rows":[
{"key":"i686-slc5-gcc43-dbg","value":"2017-06-01"},
{"key":"i686-slc5-gcc43-opt","value":"2017-06-01"},
{"key":"slc4_amd64_gcc34","value":"2014-09-10"},
{"key":"slc4_ia32_gcc34","value":"2014-09-10"},
{"key":"win32_vc71_dbg","value":"2014-09-10"},
{"key":"x86_64-centos-gcc62-dbg","value":"2017-08-04"},
{"key":"x86_64-centos-gcc62-opt","value":"2017-08-04"},
{"key":"x86_64-centos-gcc7-dbg","value":"2017-08-04"},
{"key":"x86_64-centos-gcc7-opt","value":"2017-08-04"},
{"key":"x86_64-centos7-gcc49-dbg","value":"2017-11-29"},
{"key":"x86_64-centos7-gcc49-opt","value":"2017-11-29"},
{"key":"x86_64-centos7-gcc62-dbg","value":"2018-02-01"},
{"key":"x86_64-centos7-gcc62-do0","value":"2018-02-01"},
{"key":"x86_64-centos7-gcc62-opt","value":"2018-02-01"},
{"key":"x86_64-centos7-gcc7-dbg","value":"2017-12-22"},
{"key":"x86_64-centos7-gcc7-do0","value":"2017-08-30"},
{"key":"x86_64-centos7-gcc7-opt","value":"2017-12-22"},
{"key":"x86_64-cerntos7-gcc62-opt","value":"2017-04-25"},
{"key":"x86_64-slc5-gcc43-dbg","value":"2017-06-02"},
{"key":"x86_64-slc5-gcc43-opt","value":"2017-06-02"},
{"key":"x86_64-slc5-gcc46-dbg","value":"2017-06-02"},
{"key":"x86_64-slc5-gcc46-opt","value":"2017-06-02"},
{"key":"x86_64-slc5-icc11-dbg","value":"2017-06-01"},
{"key":"x86_64-slc5-icc11-opt","value":"2017-06-01"},
{"key":"x86_64-slc6-gcc46-dbg","value":"2017-06-01"},
{"key":"x86_64-slc6-gcc46-opt","value":"2017-06-01"},
{"key":"X86_64-slc6-gcc46-opt","value":"2014-12-05"},
{"key":"x86_64-slc6-gcc48-dbg","value":"2018-01-18"},
{"key":"x86_64-slc6-gcc48-do0","value":"2017-11-13"},
{"key":"x86_64-slc6-gcc48-opt","value":"2018-01-18"},
{"key":"x86_64-slc6-gcc49-dbg","value":"2018-02-01"},
{"key":"x86_64-slc6-gcc49-do0","value":"2018-02-01"},
{"key":"x86_64-slc6-gcc49-opt","value":"2018-02-05"},
{"key":"x86_64-slc6-gcc62-dbg","value":"2018-02-01"},
{"key":"x86_64-slc6-gcc62-do0","value":"2018-02-01"},
{"key":"x86_64-slc6-gcc62-opt","value":"2018-02-01"},
{"key":"x86_64+avx-centos7-gcc62-opt+o3","value":"2017-03-16"},
{"key":"x86_64+avx2+fma-centos7-gcc62-dbg","value":"2017-09-29"},
{"key":"x86_64+avx2+fma-centos7-gcc62-opt","value":"2018-02-01"},
{"key":"<marker>","value":"2018-02-01"}
]}'''


def test_get_binary_tags():
    import LbPlatformUtils.describe

    open._overrides[LbPlatformUtils.describe.BINARY_TAGS_CACHE] = \
        BINARY_TAGS_DATA.replace('<marker>', 'from-cache-file')

    expected = [
        u'i686-slc5-gcc43-dbg', u'i686-slc5-gcc43-opt',
        u'x86_64-centos-gcc62-dbg', u'x86_64-centos-gcc62-opt',
        u'x86_64-centos-gcc7-dbg', u'x86_64-centos-gcc7-opt',
        u'x86_64-centos7-gcc49-dbg', u'x86_64-centos7-gcc49-opt',
        u'x86_64-centos7-gcc62-dbg', u'x86_64-centos7-gcc62-do0',
        u'x86_64-centos7-gcc62-opt', u'x86_64-centos7-gcc7-dbg',
        u'x86_64-centos7-gcc7-do0', u'x86_64-centos7-gcc7-opt',
        u'x86_64-cerntos7-gcc62-opt', u'x86_64-slc5-gcc43-dbg',
        u'x86_64-slc5-gcc43-opt', u'x86_64-slc5-gcc46-dbg',
        u'x86_64-slc5-gcc46-opt', u'x86_64-slc5-icc11-dbg',
        u'x86_64-slc5-icc11-opt', u'x86_64-slc6-gcc46-dbg',
        u'x86_64-slc6-gcc46-opt', u'X86_64-slc6-gcc46-opt',
        u'x86_64-slc6-gcc48-dbg', u'x86_64-slc6-gcc48-do0',
        u'x86_64-slc6-gcc48-opt', u'x86_64-slc6-gcc49-dbg',
        u'x86_64-slc6-gcc49-do0', u'x86_64-slc6-gcc49-opt',
        u'x86_64-slc6-gcc62-dbg', u'x86_64-slc6-gcc62-do0',
        u'x86_64-slc6-gcc62-opt', u'x86_64+avx-centos7-gcc62-opt+o3',
        u'x86_64+avx2+fma-centos7-gcc62-dbg',
        u'x86_64+avx2+fma-centos7-gcc62-opt', u'from-cache-file'
    ]
    assert LbPlatformUtils.describe.allBinaryTags() == expected

    try:
        import urllib.request as ul
    except ImportError:
        import urllib2 as ul
    open._overrides[LbPlatformUtils.describe.BINARY_TAGS_CACHE] = None
    ul.urlopen._overrides[LbPlatformUtils.describe.BINARY_TAGS_URL] = \
        BINARY_TAGS_DATA.replace('<marker>', 'from-url').encode()

    expected[-1] = 'from-url'
    assert LbPlatformUtils.describe.allBinaryTags() == expected

    open._overrides['/some/random/file'] = json.dumps({
        'rows': [
            {
                'key': 'none',
                'value': '1970-01-01'
            },
            {
                'key': 'x86_64-slc6-gcc62-opt',
                'value': '2018-02-01'
            },
            {
                'key': 'x86_64-centos9-gcc9-opt',
                'value': '2020-12-31'
            },
        ]
    })
    assert LbPlatformUtils.describe.allBinaryTags('/some/random/file') == [
        'x86_64-slc6-gcc62-opt', 'x86_64-centos9-gcc9-opt'
    ]

    try:
        import pkg_resources
        pkg_resources._resource_string_orig = pkg_resources.resource_string
        pkg_resources.resource_string = (
            lambda *args: BINARY_TAGS_DATA.replace('<marker>',
                                                   'from-resources').encode()
        )
        ul.urlopen._overrides[LbPlatformUtils.describe.BINARY_TAGS_URL] =\
            None
        expected[-1] = 'from-resources'
        assert LbPlatformUtils.describe.allBinaryTags() == expected

    finally:
        pkg_resources.resource_string = pkg_resources._resource_string_orig


def test_platform_info():
    from LbPlatformUtils.describe import platform_info
    # FIXME: This is just to get 100% coverage
    assert 'dirac_platform' in platform_info()
    assert 'dirac_platform' in platform_info([])


def test_script():
    import platform
    platform._system = 'Linux'
    platform._linux_dist_short = ('centos', '7.4.1708', 'Core')
    open._overrides['/etc/centos-release'] = \
        'CentOS Linux release 7.4.1708 (Core)\n'

    # let's pretend we are on a supported platform
    import sys
    del sys.modules['LbPlatformUtils']
    del sys.modules['LbPlatformUtils.inspect']
    del sys.modules['LbPlatformUtils.describe']
    from LbPlatformUtils.describe import main
    main(args=[])

    main(args=['--flags'])

    open._overrides['/some/random/file'] = json.dumps({
        'rows': [
            {
                'key': 'none',
                'value': '1970-01-01'
            },
            {
                'key': 'x86_64-slc6-gcc62-opt',
                'value': '2018-02-01'
            },
            {
                'key': 'x86_64-centos9-gcc9-opt',
                'value': '2020-12-31'
            },
        ]
    })
    main(args=['--platforms-list', '/some/random/file'])

    main(args=['--raw'])
    main(args=['--raw', '--flags'])

    try:
        main(args=['--platforms-list', '/some/random/file', '--no-platforms'])
        assert False, 'exception expected'
    except SystemExit:
        pass


def test_host_binary_tag_script():
    import platform
    platform._system = 'Linux'
    platform._linux_dist_short = ('centos', '7.4.1708', 'Core')
    open._overrides['/etc/centos-release'] = \
        'CentOS Linux release 7.4.1708 (Core)\n'

    # let's pretend we are on a supported platform
    import sys
    del sys.modules['LbPlatformUtils']
    del sys.modules['LbPlatformUtils.inspect']
    del sys.modules['LbPlatformUtils.describe']
    from LbPlatformUtils.describe import host_binary_tag_script
    host_binary_tag_script(args=[])
