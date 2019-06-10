from unittest import TestCase
from chibi.snippet import is_type
from chibi.pipeline.xml import Remove_xml_garage

example = {
    'nmaprun': {
        '@scanner': 'nmap', '@args': 'nmap',
        '@start': '1556152447',
        '@startstr': 'Wed Apr 24 19:34:07 2019',
        '@version': '7.70',
        '@xmloutputversion': '1.04',
        'verbose': { '@level': '0' },
        'debugging': { '@level': '0' }, }
}

expected = {
    'nmaprun': {
        'scanner': 'nmap', 'args': 'nmap',
        'start': '1556152447',
        'startstr': 'Wed Apr 24 19:34:07 2019',
        'version': '7.70',
        'xmloutputversion': '1.04',
        'verbose': { 'level': '0' },
        'debugging': { 'level': '0' }, }
}

class Test_pipeline( TestCase ):

    def test_should_remove_xml_garbage( self ):
        result = Remove_xml_garage().run( example )
        self.assertEqual( result, expected )
