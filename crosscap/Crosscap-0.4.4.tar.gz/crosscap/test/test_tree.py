"""
Tests of the tree decorators in kleinish
"""
from inspect import cleandoc

from pytest import inlineCallbacks

from mock import Mock

from crosscap import tree
from crosscap.test.conftest import TopApp


@inlineCallbacks
def test_enter():
    """
    Do I return a subKlein resource when I access the subTree endpoint?
    Do I also run the code in the endpoint?
    """
    top = TopApp()
    mRequest = Mock()
    res = yield top.app.execute_endpoint('subTree', mRequest)
    assert 'end' in res._app.endpoints
    mRequest.setHeader.assert_called_once_with(
            'content-type',
            'application/topapp')

    res = yield res._app.execute_endpoint('end', Mock())
    assert res == 'ended'


def test_openapiDoc():
    """
    Do I update the function I'm called with?
    """
    def fn():
        """
        This function has some stuff for sure
        ---
        a: b
        """
    fn = tree.openAPIDoc(foo={'c': 'd'})(fn)
    expected = cleandoc('''
        This function has some stuff for sure
        ---
        a: b
        ---
        foo:
          c: d
        ''') + '\n'
    assert fn.__doc__ == expected
