##################################################################################
#  SENSIML CONFIDENTIAL                                                          #
#                                                                                #
#  Copyright (c) 2017  SensiML Corporation.                                      #
#                                                                                #
#  The source code contained or  described  herein and all documents related     #
#  to the  source  code ("Material")  are  owned by SensiML Corporation or its   #
#  suppliers or licensors. Title to the Material remains with SensiML Corpora-   #
#  tion  or  its  suppliers  and  licensors. The Material may contain trade      #
#  secrets and proprietary and confidential information of SensiML Corporation   #
#  and its suppliers and licensors, and is protected by worldwide copyright      #
#  and trade secret laws and treaty provisions. No part of the Material may      #
#  be used,  copied,  reproduced,  modified,  published,  uploaded,  posted,     #
#  transmitted, distributed,  or disclosed in any way without SensiML's prior    #
#  express written permission.                                                   #
#                                                                                #
#  No license under any patent, copyright,trade secret or other intellectual     #
#  property  right  is  granted  to  or  conferred upon you by disclosure or     #
#  delivery of the Materials, either expressly, by implication,  inducement,     #
#  estoppel or otherwise.Any license under such intellectual property rights     #
#  must be express and approved by SensiML in writing.                           #
#                                                                                #
#  Unless otherwise agreed by SensiML in writing, you may not remove or alter    #
#  this notice or any other notice embedded in Materials by SensiML or SensiML's #
#  suppliers or licensors in any way.                                            #
#                                                                                #
##################################################################################


class BaseMethodCall(object):
    """The base class for calls to functions.
    Child classes have their own additional properties and overwrite this docstring.
    """

    def __init__(self, name='', function_type=''):
        self._name = name
        self._type = function_type

    def _public_properties(self):
        """Returns the object's public properties, i.e. those that do not start with _"""
        return (name for name in dir(self) if not name.startswith('_'))

    def _to_dict(self):
        prop_dict = {}
        prop_dict['inputs'] = {}
        for prop in self._public_properties():
            if getattr(self, prop) is not None:
                prop_dict['inputs'][prop] = getattr(self, prop)
        prop_dict['name'] = self._name
        return prop_dict
