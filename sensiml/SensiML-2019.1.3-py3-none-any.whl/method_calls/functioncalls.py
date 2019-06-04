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


class FunctionCalls(object):
    """Collection of function calls"""

    def __init__(self):
        self._name = ''
        self._function_calls = []

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def function_calls(self):
        return self._function_calls

    def add_function_call(self, function_call):
        """Adds a function call to the collection.

            Args:
                function_call (FunctionCall): object to append
        """
        self._function_calls.append(function_call)

    def remove_function_call(self, function_call):
        """Removes a function call from the collection.

            Args:
                function_call (FunctionCall): object to remove
        """
        self._function_calls = [
            f for f in self._function_calls if f != function_call]

    def _to_list(self):
        fcalls = []
        for item in self.function_calls:
            fcalls.append(item._to_dict())
        return fcalls

        #fcalls['name'] = self.name
        #fcalls['type'] = 'transform'
        #query_dict['outputs'] = [self.outputs]
