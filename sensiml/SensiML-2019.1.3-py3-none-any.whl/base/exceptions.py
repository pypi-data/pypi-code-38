##################################################################################
#  SENSIML CONFIDENTIAL                                                          #
#                                                                                #
#  Copyright (c) 2017-18  SensiML Corporation.                                   #
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


class DskException(Exception):
    """Base KB_DSK_Basic Exception"""
    pass


class QueryExistsException(DskException):
    pass


class BadArgumentException(DskException):
    pass


class BackendErrorException(DskException):
    pass


class FeatureFileExistsException(DskException):
    def __init__(self):
        Exception.__init__(
            self, 'FeatureFile already exists. Use force=True to override.')


class PipelineOrderException(Exception):
    pass


class PipelineDataColumnsException(Exception):
    def __init__(self):
        msg = """Warning: Binary generation is currently only possible for the following sensors:
* ACCELEROMETERX
* ACCELEROMETERY
* ACCELEROMETERZ
* GYROSCOPEX
* GYROSCOPEY
* GYROSCOPEZ
If you are using these sensors but have different names, change the column
names of your data to align with the above to generate device code."""
        print(msg)


class DuplicateValueError(Exception):
    def __init__(self, message='Duplicate values used'):
        super(DuplicateValueError, self).__init__(message)
