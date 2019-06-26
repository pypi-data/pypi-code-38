import csv
from collections import OrderedDict
from io import StringIO

from ocdsextensionregistry import Codelist, CodelistCode

content = """Code,Title,Description
open,Open,All interested suppliers may submit a tender.
selective,Selective,Only qualified suppliers are invited to submit a tender.
limited,Limited,The procuring entity contacts a number of suppliers of its choice.
direct,Direct,The contract is awarded to a single supplier without competition.
"""


def test_init():
    obj = Codelist('test.csv')

    assert obj.name == 'test.csv'
    assert obj.rows == []


def test_getitem():
    obj = fixture()

    assert obj[0] == CodelistCode(OrderedDict([
        ('Code', 'open'),
        ('Title', 'Open'),
        ('Description', 'All interested suppliers may submit a tender.'),
    ]), 'OCDS Core')


def test_iter():
    obj = fixture()
    for i, row in enumerate(obj):
        assert row == obj.rows[i]

    assert i == 3


def test_len():
    obj = fixture()

    assert len(obj) == 4


def test_repr():
    obj = fixture()

    assert repr(obj) == "Codelist(name='test.csv', rows=[CodelistCode(data=OrderedDict([('Code', 'open'), ('Title', 'Open'), ('Description', 'All interested suppliers may submit a tender.')]), extension_name='OCDS Core'), CodelistCode(data=OrderedDict([('Code', 'selective'), ('Title', 'Selective'), ('Description', 'Only qualified suppliers are invited to submit a tender.')]), extension_name='OCDS Core'), CodelistCode(data=OrderedDict([('Code', 'limited'), ('Title', 'Limited'), ('Description', 'The procuring entity contacts a number of suppliers of its choice.')]), extension_name='OCDS Core'), CodelistCode(data=OrderedDict([('Code', 'direct'), ('Title', 'Direct'), ('Description', 'The contract is awarded to a single supplier without competition.')]), extension_name='OCDS Core')])"  # noqa


def test_extend():
    obj = fixture()
    obj.extend(csv.DictReader(StringIO('Code\nother')), 'Other')
    obj.extend(csv.DictReader(StringIO('Code\nanother')))

    assert obj.rows == [
        CodelistCode(OrderedDict([
            ('Code', 'open'),
            ('Title', 'Open'),
            ('Description', 'All interested suppliers may submit a tender.'),
        ]), 'OCDS Core'),
        CodelistCode(OrderedDict([
            ('Code', 'selective'),
            ('Title', 'Selective'),
            ('Description', 'Only qualified suppliers are invited to submit a tender.'),
        ]), 'OCDS Core'),
        CodelistCode(OrderedDict([
            ('Code', 'limited'),
            ('Title', 'Limited'),
            ('Description', 'The procuring entity contacts a number of suppliers of its choice.'),
        ]), 'OCDS Core'),
        CodelistCode(OrderedDict([
            ('Code', 'direct'),
            ('Title', 'Direct'),
            ('Description', 'The contract is awarded to a single supplier without competition.'),
        ]), 'OCDS Core'),
        CodelistCode(OrderedDict([
            ('Code', 'other'),
        ]), 'Other'),
        CodelistCode(OrderedDict([
            ('Code', 'another'),
        ])),
    ]


def test_fieldnames():
    obj = fixture()
    obj.extend(csv.DictReader(StringIO('Code,Deprecated\nother,1.1')), 'Other')

    assert obj.fieldnames == ['Code', 'Title', 'Description', 'Deprecated']


def test_add_extension_column():
    obj = fixture()
    obj.extend(csv.DictReader(StringIO('Code\nother')), 'Other')
    obj.add_extension_column('Extension Name')

    assert obj.rows[0]['Extension Name'] == 'OCDS Core'
    assert obj.rows[-1]['Extension Name'] == 'Other'


def test_remove_deprecated_codes():
    obj = fixture()
    obj.extend(csv.DictReader(StringIO('Code,Deprecated\nother,1.1')), 'Other')
    obj.remove_deprecated_codes()

    assert 'open' in obj.codes
    assert 'other' not in obj.codes


def test_codes():
    obj = fixture()

    assert obj.codes == ['open', 'selective', 'limited', 'direct']


def test_basename():
    for name in ('test.csv', '+test.csv', '-test.csv'):
        obj = Codelist(name)

        assert obj.basename == 'test.csv'


def test_patch():
    for i, name in enumerate(('test.csv', '+test.csv', '-test.csv')):
        obj = Codelist(name)

        assert not i and not obj.patch or i and obj.patch


def test_addend():
    for i, name in enumerate(('+test.csv', 'test.csv', '-test.csv')):
        obj = Codelist(name)

        assert not i and obj.addend or i and not obj.addend


def test_subtrahend():
    for i, name in enumerate(('-test.csv', 'test.csv', '+test.csv')):
        obj = Codelist(name)

        assert not i and obj.subtrahend or i and not obj.subtrahend


def fixture():
    obj = Codelist('test.csv')
    obj.extend(csv.DictReader(StringIO(content)), 'OCDS Core')
    return obj
