'''
Created on 09/07/2014

@author: synerty
'''

from vortex.Tuple import addTupleType, Tuple, TupleField


@addTupleType
class PeekAdmNavbarUserTuple(Tuple):
    __tupleType__ = 'peek_server.PeekAdmNavbarUserTuple'

    supportExceeded = TupleField(False)
    demoExceeded = TupleField(False)
    countsExceeded = TupleField(False)
    username = TupleField('nouser')