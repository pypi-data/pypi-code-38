# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


from steelscript.steelhead.core.steelhead import SteelHead


def new_device_instance(*args, **kwargs):
    # Used by DeviceManager to create a SteelHead instance
    return SteelHead(*args, **kwargs)
