#!/usr/bin/env python
#
# test_custom.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import textwrap as tw

import pytest

import funpack.custom as custom

from . import tempdir, clear_plugins


@clear_plugins
def test_register():

    ran = {}

    custom.registry.clearRegistry()

    @custom.loader('test_loader')
    def custom_loader():
        ran['loader'] = True

    @custom.sniffer('test_sniffer')
    def custom_sniffer():
        ran['sniffer'] = True

    @custom.formatter('test_formatter')
    def custom_formatter():
        ran['formatter'] = True

    @custom.cleaner('test_cleaner')
    def custom_cleaner():
        ran['cleaner'] = True

    @custom.processor('test_processor')
    def custom_processor():
        ran['processor'] = True

    @custom.exporter()
    def exporter1():
        ran['exporter1'] = True

    @custom.registerPlugin('exporter', 'test_exporter2')
    def exporter2():
        ran['exporter2'] = True

    with pytest.raises(ValueError):
        @custom.registerPlugin('bad_type')
        def bad_plugin():
            pass

    assert custom.listPlugins('loader')    == ['test_loader']
    assert custom.listPlugins('sniffer')   == ['test_sniffer']
    assert custom.listPlugins('formatter') == ['test_formatter']
    assert custom.listPlugins('cleaner')   == ['test_cleaner']
    assert custom.listPlugins('processor') == ['test_processor']
    assert custom.listPlugins('exporter')  == ['exporter1', 'test_exporter2']

    assert custom.exists('loader',    'test_loader')
    assert custom.exists('sniffer',   'test_sniffer')
    assert custom.exists('formatter', 'test_formatter')
    assert custom.exists('cleaner',   'test_cleaner')
    assert custom.exists('processor', 'test_processor')
    assert custom.exists('exporter',  'exporter1')
    assert custom.exists('exporter',  'test_exporter2')

    custom.run('loader',    'test_loader')
    custom.run('sniffer',   'test_sniffer')
    custom.run('formatter', 'test_formatter')
    custom.run('cleaner',   'test_cleaner')
    custom.run('processor', 'test_processor')
    custom.run('exporter',  'exporter1')
    custom.run('exporter',  'test_exporter2')

    assert ran['loader']
    assert ran['sniffer']
    assert ran['formatter']
    assert ran['cleaner']
    assert ran['processor']
    assert ran['exporter1']
    assert ran['exporter2']


@clear_plugins
def test_loadPluginFile():

    contents = tw.dedent("""

    import funpack.custom as custom

    @custom.cleaner('poo')
    def poo():
        pass
    """).strip()

    with tempdir():

        with open('plugin.py', 'wt') as f:
            f.write(contents)

        custom.loadPluginFile('plugin.py')
        assert custom.exists('cleaner', 'poo')

    # also load a built-in plugin file
    custom.loadPluginFile('fmrib.py')
    assert custom.exists('formatter', 'FMRIBImagingDate')
