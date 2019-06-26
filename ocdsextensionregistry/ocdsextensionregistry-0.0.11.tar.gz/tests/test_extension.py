from ocdsextensionregistry import Extension


def test_init():
    args = arguments(Core='true')
    obj = Extension(args)

    assert obj.id == args['Id']
    assert obj.category == args['Category']
    assert obj.core is True


def test_init_non_core():
    for core in ('TRUE', 'True', 'false', 'foo', '', None):
        obj = Extension(arguments(Core=core))

        assert obj.core is False


def test_as_dict():
    args = arguments(Core='')
    obj = Extension(args)

    assert obj.as_dict() == {
        'id': args['Id'],
        'category': args['Category'],
        'core': False,
    }


def arguments(**kwargs):
    data = {
        'Id': 'location',
        'Category': 'item',
    }

    data.update(kwargs)
    return data
