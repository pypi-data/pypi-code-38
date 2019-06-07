# coding=utf-8
"""
Tests of the doc class
"""
from builtins import object

from crosscap import doc


def test_doc():
    """
    Does the doc function return the first line?
    """
    def aFunction(): # pragma: nocover
        """
        Hello

        there
        """

    assert doc.doc(aFunction) == "Hello"


def test_documentation():
    """
    Do I find the doc on an object?

    Do I extract first the first line?

    Do I decode if asked to?
    """
    class Cls(object):
        """
        I have a bytestr docstring

        It is 2 lines
        """

    class Unicls(object):
        u"""
        I have a unicode docstring
        """

    class StrClsWithUTF8(object):
        """
        I have a 😼💫 docstring
        """

    assert doc.doc(Cls) == "I have a bytestr docstring"

    assert doc.Documentation.fromObject(Cls).full == "I have a bytestr docstring\n\nIt is 2 lines"
    assert type(doc.Documentation.fromObject(Unicls).first) is type(u'')
    strDoc = doc.Documentation.fromObject(StrClsWithUTF8, decode=True)
    assert strDoc.first == u'I have a 😼💫 docstring'
    assert type(strDoc.first) is type(u'')
