__copyright__ = "# Copyright (c) 2016 by cisco Systems, Inc. All rights reserved."
__author__ = "Giacomo Trifilo <gtrifilo@cisco.com>"


from unicon.plugins.generic.service_implementation import \
    Execute as GenericExecute
from unicon.eal.dialogs import Dialog
from unicon.plugins.iosxe.service_statements import confirm


class Execute(GenericExecute):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.dialog += Dialog([confirm])
