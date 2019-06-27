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

import warnings


class DeviceConfig(dict):
    """
    Defines dictionary class for device configuration to be sent from sensiml to the
    Server for KnowledgePack code/binary generation.
    """

    # List of fields and their defaults
    fields = {
        'target_platform': 0,
        'build_flags': '',
        'budget': {},
        'debug': False,
        'sram_size': None,
        'test_data': '',
        'application': '',
        'sample_rate': 100,
        'kb_description': None,
    }

    def __init__(self, iterable=None, strict=True, **kwargs):
        super(DeviceConfig, self).__init__()
        object.__setattr__(self, '_strict', strict)
        for k, v in self.fields.items():
            self[k] = v
        if iterable:
            for k, v in dict(iterable).items():
                setattr(self, k, v)
        if kwargs:
            for k, v in kwargs.items():
                setattr(self, k, v)

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if self._strict and name not in self.fields.keys():
            out_str = '{} not in device configuration.'.format(name)
            out_str += '\nYou may need to update the device configuration on KB Cloud.'
            warnings.warn(out_str, DeprecationWarning)

            return
        if name == 'budget':
            assert isinstance(value, dict), 'Budget is not a dictionary.'
        elif name == 'debug':
            value = bool(value)

        self[name] = value

    def initialize_from_dict(self, init_dict):
        """DEPRECATED: Populates a single device config from a dictionary of properties.

            Args:
                (dict): contains target_platform, platform_version, build_flags, budget, debug and sram_size
        """
        warnings.warn(
            'initialize_from_dict() is deprecated. Please pass arguments to constructor', DeprecationWarning)
        for k, v in init_dict.items():
            setattr(self, k, v)
