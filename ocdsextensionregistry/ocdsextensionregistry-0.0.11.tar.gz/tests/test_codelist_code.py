import pytest

from ocdsextensionregistry import CodelistCode


def test_init():
    obj = CodelistCode(*arguments())

    assert obj.data == {'Code': 'tender', 'Title': 'Tender', 'Description': '…'}
    assert obj.extension_name is None


def test_init_extension_name():
    obj = CodelistCode(*arguments('OCDS Core'))

    assert obj.data == {'Code': 'tender', 'Title': 'Tender', 'Description': '…'}
    assert obj.extension_name == 'OCDS Core'


def test_eq():
    obj = CodelistCode(*arguments())

    assert obj == CodelistCode(*arguments())


def test_eq_dict():
    args = arguments()
    obj = CodelistCode(*args)

    assert obj == args[0]


def test_getitem():
    obj = CodelistCode(*arguments())

    assert obj['Code'] == 'tender'

    with pytest.raises(KeyError) as excinfo:
        obj['nonexistent']

    assert str(excinfo.value) == "'nonexistent'"


def test_get():
    obj = CodelistCode(*arguments())

    assert obj.get('Code') == 'tender'

    assert obj.get('nonexistent', 'default') == 'default'


def test_setitem():
    obj = CodelistCode(*arguments())
    obj['Extension'] = 'OCDS Core'

    assert obj['Extension'] == 'OCDS Core'


def test_iter():
    obj = CodelistCode(*arguments())
    for i, item in enumerate(obj):
        pass

    assert i == 2


def test_len():
    obj = CodelistCode(*arguments())

    assert len(obj) == 3


def test_repr():
    obj = CodelistCode(*arguments())

    assert repr(obj) == "CodelistCode(data={'Code': 'tender', 'Title': 'Tender', 'Description': '…'})"


def test_repr_extension_name():
    obj = CodelistCode(*arguments('OCDS Core'))

    assert repr(obj) == "CodelistCode(data={'Code': 'tender', 'Title': 'Tender', 'Description': '…'}, extension_name='OCDS Core')"  # noqa


def test_pop():
    obj = CodelistCode(*arguments())

    assert obj.pop('Code', 'default') == 'tender'

    assert obj.pop('Code', 'default') == 'default'

    with pytest.raises(KeyError) as excinfo:
        obj['Code']

    assert str(excinfo.value) == "'Code'"


def arguments(*args):
    data = [{'Code': 'tender', 'Title': 'Tender', 'Description': '…'}]

    data.extend(args)
    return data
