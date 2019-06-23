import xml.etree.ElementTree as ET
from datetime import datetime
from bebanjo.xml_utils import _append_elements


def test_append_elements():
    root = ET.Element('root')
    data = {
        'myint': 15,
        'mystr': 'a_string',
        'myints': [1, 2],
        'mystrs': ['one', 'two'],
        'dt_gmt': datetime(2019, 1, 1, 12),
        'my_dst': datetime(2019, 6, 1, 12)
    }
    _append_elements(root, data)
    r = ET.tostring(root)
    assert r == b'<root><myint type="integer">15</myint><mystr>a_string</mystr><myints type="array"><myint type="integer">1</myint><myint type="integer">2</myint></myints><mystrs type="array"><mystr>one</mystr><mystr>two</mystr></mystrs><dt-gmt type="datetime">2019-01-01T12:00:00</dt-gmt><my-dst type="datetime">2019-06-01T12:00:00</my-dst></root>'  # pylint: disable=line-too-long
