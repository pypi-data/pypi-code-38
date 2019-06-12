# -*- coding: utf-8 -*-
# Copyright 2006 St James Software

"""Tests for the IterativeTester framework. Also serves as a usage example.
   Framework is used as follows:
     * Create or import some Dimension classes (Dimensions for common resources
       like databases, webservers, etc should be provided as part of the testing
       framework)
     * Subclass IterativeTester and populate the class attribute DIMENSIONS with
       information about what prefixes you're using for tests which need to be
       iterated over and the Dimensions which supply their arguments.
"""

from j5test.IterativeTester import IterativeTester, Dimension
from j5test.Utils import raises

#
# Dimensions
#

class WebServer_Dim1(Dimension):
    def __init__(self):
        self._resources = { 'webA' : 1, 'webB' : 2 }

    def setup_method(self, varname):
        self._resources[varname] += 10

    def teardown_method(self, varname):
        self._resources[varname] -= 10

class Databases_Dim2(Dimension):
    def __init__(self):
        self._resources = { 'dbA' : 3, 'dbB' : 4 }

#
# Basic Test
#

class TestExample(IterativeTester):
    DIMENSIONS = { 'webdb_test' : [WebServer_Dim1(), Databases_Dim2()],
                   'dbonly_test' : [Databases_Dim2()] }

    def webdb_test_A(self,webserver,db):
        print("A", webserver, db)

    # Check existing method
    def test_A_webA_dbA(self):
        print("A", "existing webA", "existing dbA")

    def webdb_test_B(self,webserver,db):
        print("B", webserver, db)

    def checkdb(self, db):
        assert db == 3

    def dbonly_test_C(self,db):
        print("C", db)
        if db != 3:
            assert raises(AssertionError, self.checkdb, db)
        else:
            self.checkdb(db)

    def dbonly_test_iterdata(self,db):
        """Check we copy the docstring with this"""
        assert self.iterdata.db == db

    def webdb_test_iterdata(self,web,db):
        assert self.iterdata.db == db
        assert self.iterdata.web == web

    def webdb_test_setupmethod(self, webserver, db):
        assert self.inwebdb
        assert hasattr(self, "methodname")
        assert self.methodname.startswith("test_setupmethod")
        assert self.expectedweb == webserver
        assert self.expecteddb == db
        assert webserver in (11,12)
        assert db in (3,4)

    @classmethod
    def setup_class(cls):
        print("We expect to find 16 tests")
        super(TestExample,cls).setup_class()

    @classmethod
    def setup_class_webdb_test(cls,webserver,db):
        print("Setup class:", webserver, db)

    def testSomeOtherThing(self):
        assert True

    def setup_method_webdb_test(self, method, webserver, db):
        print("Setup method for webdb...")
        print("\t", method.__name__)
        print("\t", method.iterativetestvarnames)
        print("\t", method.iterativetestprefix)
        self.inwebdb = True
        self.methodname = method.__name__
        self.expectedweb = webserver
        self.expecteddb = db
        self.iterdata.web = webserver
        self.iterdata.db = db

    def setup_method_dbonly_test(self, method, db):
        print("Setup method for dbonly...")
        print("\t", method.iterativetestprefix)
        self.iterdata.db = db

    def teardown_method_webdb_test(self, method, webserver, db):
        print("Teardown method for webdb...")
        self.inwebdb = False
        self.methodname = None
        self.expectedweb = None
        self.expecteddb = None

#
# Inheritance Test
#

class IterativeTesterA(IterativeTester):
    def someprefix_test1(self,web):
        assert True

class IterativeTesterB(IterativeTesterA):
    DIMENSIONS = { 'someprefix' : [WebServer_Dim1()] }

class TestInheritance(object):
    def test_methods_exist(self):
        assert getattr(IterativeTesterB,'test_test1_webA',None) is not None
        assert getattr(IterativeTesterB,'test_test1_webB',None) is not None

