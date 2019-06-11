__all__ = ['assert_exc', 'raise_exc']


def assert_exc(value, message):
    if not value:
        raise Exception(message)


def raise_exc(message):
    raise Exception(message)


def check_dict_and_assert(obj_name, obj, fields):
    assert_exc(obj, f'{obj_name} cannot be null')
    for item in fields:
        assert_exc(obj.get(item), f'{obj_name}["{item}"] cannot be null')


def check_object_and_assert(obj_name, obj, fields):
    assert_exc(obj, f'{obj_name} cannot be null')
    for item in fields:
        assert_exc(
            getattr(obj, item, None), f'{obj_name}.{item} cannot be null'
        )
