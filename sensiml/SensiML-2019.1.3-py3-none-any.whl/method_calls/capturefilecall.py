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


from sensiml.datamanager.pipeline import PipelineStep


class CaptureFileCall(PipelineStep):
    """The base class for a featurefile call"""

    def __init__(self, name):
        super(CaptureFileCall, self).__init__(
            name=name, step_type='CaptureFileCall')
        self.name = name
        self._data_columns = None
        self._group_columns = ['Subject']

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if not isinstance(name, list):
            name = [name]
        self._name = name

    @property
    def data_columns(self):
        return self._data_columns

    @data_columns.setter
    def data_columns(self, value):
        self._data_columns = value

    @property
    def outputs(self):
        return self._outputs

    @outputs.setter
    def outputs(self, outputs):
        self._outputs = outputs

    @property
    def group_columns(self):
        return self._group_columns

    @group_columns.setter
    def group_columns(self, value):
        print("Capture files default to Subject.")

    def _to_dict(self):
        capturefile_dict = {}
        capturefile_dict['name'] = self.name
        capturefile_dict['type'] = 'capturefile'
        capturefile_dict['data_columns'] = getattr(self, '_data_columns')
        capturefile_dict['group_columns'] = getattr(self, '_group_columns')
        capturefile_dict['outputs'] = getattr(self, '_outputs')
        return capturefile_dict
