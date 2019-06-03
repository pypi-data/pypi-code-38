import collections
import sys

import pytest

from . import renew


class PlainObject(object):
    def __init__(self, the_argument):
        self.the_argument = the_argument


@pytest.mark.parametrize("namespace, expected_statement", [
    (None, "renew.test_renew.PlainObject(3.14159)"),
    ("", "PlainObject(3.14159)"),
    ("any.name.space", "any.name.space.PlainObject(3.14159)"),
])
def test_namespaces_module(namespace, expected_statement):
    decorator = renew.reproducible(namespace=namespace)
    cls = decorator(PlainObject)
    assert repr(cls(3.14159)) == expected_statement


@pytest.mark.parametrize("namespace, expected_statement", [
    (None, "renew.test_renew.test_namespaces_local.<locals>.PlainLocalObject(3.14159)"),
    ("", "PlainLocalObject(3.14159)"),
    ("any.name.space", "any.name.space.test_namespaces_local.<locals>.PlainLocalObject(3.14159)"),
])
def test_namespaces_local(namespace, expected_statement):
    class PlainLocalObject:
        def __init__(self, the_argument):
            self.the_argument = the_argument

    decorator = renew.reproducible(namespace=namespace)
    cls = decorator(PlainLocalObject)
    if sys.version < '3':
        # python2 does not support __qualname__
        expected_statement = expected_statement.replace(".test_namespaces_local.<locals>", "")

    assert repr(cls(3.14159)) == expected_statement


@renew.reproducible(namespace="")
class NoArguments(object):

    def __init__(self):
        pass


@renew.reproducible(namespace="")
class Reproducible(object):

    def __init__(self, item_name, *other_arguments):
        self.item_name = item_name
        self.other_arguments = other_arguments


@pytest.mark.parametrize("statement", [
    "Reproducible(None, None)",
    "Reproducible('things')",
    "Reproducible('things', 1)",
    "Reproducible('things', 1, 2, 'nothing', 'much', 'more', None)",
])
def test_it_is_reproducible(statement):
    a = eval(statement)
    assert repr(a) == statement


def test_reproducible():
    outer = Reproducible(
        NoArguments(),
        Reproducible("this one should", 'fit inline'),
        Reproducible(
            "some string",
            Reproducible(1, 2, None),
            Reproducible((1, 2, 3), 'b6589fc6ab0dc82cf12099d1c2d40ab994e8410c',
                         'ddfe163345d338193ac2bdc183f8e9dcff904b43'),
            Reproducible([11, 12, 13, 14, 15], {}, ()),
        ),
        None,
        Reproducible("here one with dict", {
            "aa": "a_value",
            "bb": 23,
            34: None,
        }),
        Reproducible("this one will break", [
            "87acec17cd9dcd20a716cc2cf67417b71c8a7016",
            "36a27136f3015f5ed0e1fe268ad7a93a985196cf",
            "a8624bd0a5caa95e0be9cd95d4ed86a558a33553",
            "73986020e8eb281b34b88661bea3fbcd14318e3e",
        ]),
        {
            "dict_check": Reproducible(
                "Pythons dicts are not supported and this test case is",
                "just to prove how bad it is. It's syntactically valid, but",
                "you would never say that's nice (indentation fail).",
            ),
            "another key": "To ensure at least keys are sorted",
            23: "Simple items have a little chance to be ok.",
        },
    )

    expected_reproduction = """\
Reproducible(
    NoArguments(),
    Reproducible('this one should', 'fit inline'),
    Reproducible(
        'some string',
        Reproducible(1, 2, None),
        Reproducible(
            (1, 2, 3),
            'b6589fc6ab0dc82cf12099d1c2d40ab994e8410c',
            'ddfe163345d338193ac2bdc183f8e9dcff904b43',
        ),
        Reproducible([11, 12, 13, 14, 15], {}, ()),
    ),
    None,
    Reproducible('here one with dict', {34: None, 'aa': 'a_value', 'bb': 23}),
    Reproducible(
        'this one will break',
        [
            '87acec17cd9dcd20a716cc2cf67417b71c8a7016',
            '36a27136f3015f5ed0e1fe268ad7a93a985196cf',
            'a8624bd0a5caa95e0be9cd95d4ed86a558a33553',
            '73986020e8eb281b34b88661bea3fbcd14318e3e',
        ],
    ),
    {
        23: 'Simple items have a little chance to be ok.',
        'another key': 'To ensure at least keys are sorted',
        'dict_check': Reproducible(
            'Pythons dicts are not supported and this test case is',
            "just to prove how bad it is. It's syntactically valid, but",
            "you would never say that's nice (indentation fail).",
        ),
    },
)"""
    assert repr(outer) == expected_reproduction
    assert repr(eval(expected_reproduction)) == expected_reproduction


def test_bad_namespace_definition():
    with pytest.raises(ValueError, match="Namespace has to be string or None, got tuple."):
        @renew.reproducible(("insane",))
        class _(object):
            def __init__(self):
                "do not cover"


def test_bad_definition():
    @renew.reproducible("some.namespace")
    class BadDefinition(object):
        def __init__(self, valid_name):
            self.different_name = valid_name

    with pytest.raises(AttributeError, match="BadDefinition has no 'valid_name' attribute."):
        repr(BadDefinition("ok"))


class NoConstructor(object):
    pass


def test_raise_missing_ctor_at_creation_time():
    decorator = renew.reproducible("")

    with pytest.raises(TypeError, match="The class NoConstructor does not implement constructor."):
        decorator(NoConstructor)


def test_renew_set():
    r = Reproducible(
        {
            '87acec17cd9dcd20a716cc2cf67417b71c8a7016',
            '36a27136f3015f5ed0e1fe268ad7a93a985196cf',
            'a8624bd0a5caa95e0be9cd95d4ed86a558a33553',
            '73986020e8eb281b34b88661bea3fbcd14318e3e',
        },
        [{1, 2, 3}, {4, 5, 6, 7, 8}]
    )
    assert repr(r) == """\
Reproducible(
    {
        '36a27136f3015f5ed0e1fe268ad7a93a985196cf',
        '73986020e8eb281b34b88661bea3fbcd14318e3e',
        '87acec17cd9dcd20a716cc2cf67417b71c8a7016',
        'a8624bd0a5caa95e0be9cd95d4ed86a558a33553',
    },
    [{1, 2, 3}, {4, 5, 6, 7, 8}],
)"""


def test_repr_inheritance():
    class Derived(Reproducible):
        pass

    a = Derived(
        "89777c66e3f39bfe15392bb3d1c6ec51d98f8071",
        "4f1030137e25e64fd6798cbe18bd99ff64e8c94f",
        "fca200d95659e7375c5418e7bbd887dce1b11d9f",
        "2b45ed32d40683c1673bf4aaade17a55a51fbba1",
    )
    assert repr(a) == """\
Derived(
    '89777c66e3f39bfe15392bb3d1c6ec51d98f8071',
    '4f1030137e25e64fd6798cbe18bd99ff64e8c94f',
    'fca200d95659e7375c5418e7bbd887dce1b11d9f',
    '2b45ed32d40683c1673bf4aaade17a55a51fbba1',
)"""


@pytest.mark.parametrize("expression", [
    "[]", "{}", "()", "[1, 2]", "{1, 2}", "(1, 2)", "'just a string'",
    "[{1, 2, 3}, [(4, [(5, 6), 7], 8), 9.01], {10: 11, 12: 13}]", """\
{
    '327603e5417941eefa1b3a25f831a50b73375c59': 'fe11383d9e79d97573f33fb682de070ce1c706d4',
    'a96da3b51126afaba9acf291d8bb934d0cbe5905': '44a4978104be4f6a824acbf9784bb364a575fb1f',
}""", """\
{
    '327603e5417941eefa1b3a25f831a50b73375c59': {
        'fe11383d9e79d97573f33fb682de070ce1c706d4': [{1, 2, 3}, [(4, [(5, 6), 7], 8), 9.01], {10: 11, 12: 13}],
    },
}"""])
def test_repr_plain_types(expression):
    assert renew.reproduction(eval(expression)) == expression


A = collections.namedtuple("FakeArgSpec", "args, defaults")


@pytest.mark.parametrize('spec, expected_result', [
    [A(("a", "b", "c"), ()), (('a', False, None), ('b', False, None), ('c', False, None))],
    [A(("a", "b", "c"), (3,)), (('a', False, None), ('b', False, None), ('c', True, 3))],
    [A(("a", "b", "c"), (2, 3)), (('a', False, None), ('b', True, 2), ('c', True, 3))],
    [A(("a", "b", "c"), (1, None, 3)), (('a', True, 1), ('b', True, None), ('c', True, 3))],
])
def test_bind_defaults(spec, expected_result):
    assert renew._bind_defaults(spec) == expected_result


@renew.reproducible("")
class Defaults(object):
    def __init__(self, first, second=22, third=33, fourth=4.4):
        self.first, self.second, self.third, self.fourth = first, second, third, fourth


@pytest.mark.parametrize('instance, expected_repr', [
    (Defaults(1), "Defaults(1)"),
    (Defaults(1, 22), "Defaults(1)"),
    (Defaults(1, 22, 33), "Defaults(1)"),
    (Defaults(1, 22, 33, None), "Defaults(1, fourth=None)"),
    (Defaults(1, 10, 20, 30), "Defaults(1, 10, 20, 30)"),
    (Defaults(None, None, None, None), "Defaults(None, None, None, None)"),
    (Defaults(1, fourth='d', second='b', third=None), "Defaults(1, 'b', None, 'd')"),
    (Defaults(1, fourth='droppin'), "Defaults(1, fourth='droppin')"),
])
def test_default_args(instance, expected_repr):
    assert repr(instance) == expected_repr
    assert repr(eval(expected_repr)) == expected_repr


def test_raises_unsupported_signature():
    class Kws(object):
        def __init__(self, a=23, **_):
            pass

    msg = "Kws has no 'a' attribute. Constructor args have to be named same as class attributes."
    with pytest.raises(AttributeError, match=msg):
        renew.reproduction(Kws(kak=1))


def test_repr_namedtuple():
    A = collections.namedtuple('A', 'one, two, three')
    a = A(None, -3, 19)
    expected_str = "A(one=None, two=-3, three=19)"
    assert renew.reproduction(a) == expected_str
    assert eval(renew.reproduction(a)) == a


@pytest.fixture
def lorem_with_breaks():
    return "\n".join([
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt "
        "ut labore et dolore magna aliqua. Libero nunc consequat interdum varius sit. Maecenas accumsan "
        "lacus vel facilisis:",
        "  - Dui ut ornare,",
        "  - Lectus,",
        "  - Malesuada pellentesque,",
        "",
        "",
        "Elit eget gravida cum sociis natoque penatibus et. Netus et malesuada fames ac turpis egestas sed.",
        "Egestas integer eget aliquet.",
    ])


def test_repr_long_string(lorem_with_breaks):
    assert renew.reproduction(lorem_with_breaks) == r"""(
    'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt '
    'ut labore et dolore magna aliqua. Libero nunc consequat interdum varius sit. Maecenas '
    'accumsan lacus vel facilisis:\n  - Dui ut ornare,\n  - Lectus,\n  - Malesuada pellentesque,\n\n\nElit '
    'eget gravida cum sociis natoque penatibus et. Netus et malesuada fames ac turpis '
    'egestas sed.\nEgestas integer eget aliquet.'
)"""


def test_repr_text_short_lines():
    that_text = """\
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
ut labore et dolore magna aliqua. Libero nunc consequat interdum varius sit.
Maecenas accumsan lacus vel facilisis:
 - Dui ut ornare,
 - Lectus,
 - Malesuada pellentesque
"""
    assert renew.reproduction(that_text) == r"""(
    'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do\n'
    'ut labore et dolore magna aliqua. Libero nunc consequat interdum varius sit.\n'
    'Maecenas accumsan lacus vel facilisis:\n'
    ' - Dui ut ornare,\n'
    ' - Lectus,\n'
    ' - Malesuada pellentesque\n'
    ''
)"""

    assert list(renew._repr_dispatcher(that_text)) == [
        "'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do\\n'\n",
        "'ut labore et dolore magna aliqua. Libero nunc consequat interdum varius sit.\\n'\n",
        "'Maecenas accumsan lacus vel facilisis:\\n'\n",
        "' - Dui ut ornare,\\n'\n",
        "' - Lectus,\\n'\n",
        "' - Malesuada pellentesque\\n'\n",
        "''\n"
    ]
