# -*- coding: utf-8 -*-

"""Testing module for our API structure
   Also serves as a helper to understand how the API declarations etc work
"""

from j5basic import API
from j5test import Utils
from six import with_metaclass

class ArbAPI(API.API):
    def i_support_api(self):
        """I do support the API"""

class ArbAPI2(API.API):
    def i_add_value(self):
        """I do it in a worthwhile way"""

class ArbAPI3(API.API):
    def i_never_give_up(self):
        """Even if I run out of ammo"""

class ImplementingAPIClass(object):
    API.implements(ArbAPI, ArbAPI2)
    def __init__(self, value1, value2):
        """APIs can have arbritrary initialization"""
        self.value1 = value1
        self.value2 = value2

    def i_support_api(self):
        return True

    def i_add_value(self):
        return self.value1 + self.value2

class NotAnAPI(object):
    pass

class TestAPI(object):
    def test_check_implementing(self):
        """checks the sample implementing class"""
        assert API.supports(ImplementingAPIClass, ArbAPI)
        assert API.supports(ImplementingAPIClass, ArbAPI2)
        assert API.supports(ImplementingAPIClass, ArbAPI, ArbAPI2)
        assert API.supports(ImplementingAPIClass)
        assert not API.supports(ImplementingAPIClass, ArbAPI3)
        assert not API.supports(ImplementingAPIClass, ArbAPI, ArbAPI3)
        x = ImplementingAPIClass(3,4)
        assert API.supports(x, ArbAPI)
        assert API.supports(x, ArbAPI2)
        assert API.supports(x, ArbAPI, ArbAPI2)
        assert API.supports(x)
        assert not API.supports(x, ArbAPI3)
        assert not API.supports(x, ArbAPI, ArbAPI3)
        assert x.i_support_api()
        assert x.i_add_value() == 7
        assert not API.supports(ImplementingAPIClass, NotAnAPI)

    def declare_basic_support(self):
        """Check that declarations of support work if the API is implemented in parent classes"""
        class TrueAndSimple(with_metaclass(API.APIMeta, object)):
            API.implements(ArbAPI3)
            def i_never_give_up(self):
                while True:
                    yield "bottles"
        return TrueAndSimple

    def declare_inherited_support(self):
        """Check that declarations of support work if the API is implemented in parent classes"""
        class TrueChild(with_metaclass(API.APIMeta, object)):
            pass
        return TrueChild

    def declare_false_support(self):
        """Try and declare a class as implementing an API that it doesn't"""
        class LiarAndFraud(with_metaclass(API.APIMeta, object)):
            API.implements(ArbAPI)
        return LiarAndFraud

    def declare_ill_support(self):
        """Try and declare a class as implementing an API but the method signatures are wrong"""
        class SlightlyDeceptive(with_metaclass(API.APIMeta, object)):
            API.implements(ArbAPI)
            def i_support_api(self, x):
                return True
        return SlightlyDeceptive

    def declare_false_inherited_support(self):
        """Check that declarations of support fail even if the API is declared implemented in parent classes"""
        class Parent(object):
            API.implements(ArbAPI2)
        class FalseChild(with_metaclass(API.APIMeta, Parent)):
            pass
        return FalseChild

    def test_meta_declaration(self):
        """Tests that false declarations of implementing an API raise an error"""
        assert Utils.not_raises(API.APIError, self.declare_basic_support)
        assert Utils.not_raises(API.APIError, self.declare_inherited_support)
        assert Utils.raises(API.APIError, self.declare_false_support)
        assert Utils.raises(API.APIError, self.declare_false_inherited_support)
        assert Utils.raises(API.APIError, self.declare_ill_support)

