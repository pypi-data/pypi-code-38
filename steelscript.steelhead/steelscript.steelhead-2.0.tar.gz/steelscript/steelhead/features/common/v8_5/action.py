# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from __future__ import (absolute_import, unicode_literals, print_function,
                        division)

from steelscript.common.interaction import action, uidelegation


@action.action
class CommonAction(action.Action):
    """
    Kauai Actions for the 'common' REST Service on the SteelHead product.
    """


class CLI(uidelegation.CLIDelegatee):
    """
    CLI-based Actions for the 'common' REST Service on the SteelHead product.
    """

    def get_product_info(self):
        """
        Gets basic software and hardware product information.

        :return: Dictionary of values:

        .. code-block:: python

            {'name': 'SteelHead',
             'model': 'CX1555',
             'release': '9.0.1'}
        """
        version_info = self.model.show_version()
        return {'name': 'SteelHead',
                'model': version_info['product model'],
                'release': version_info['product release']}
