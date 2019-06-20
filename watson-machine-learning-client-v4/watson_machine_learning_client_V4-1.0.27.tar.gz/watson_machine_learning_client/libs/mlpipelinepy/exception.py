################################################################################
# IBM Confidential
# OCO Source Materials
# (c) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
################################################################################
'''
Created on Feb 17, 2017

@author: calin
'''

class UnsupportedNodeTypeError(Exception):
    """ Unsupported node type failure. """
    def __init__(self, *args, **kwargs): # real signature unknown
        pass

    @staticmethod # known case of __new__
    def __new__(S, *more): # real signature unknown; restored from __doc__
        """ T.__new__(S, ...) -> a new object with type S, a subtype of T """
        pass