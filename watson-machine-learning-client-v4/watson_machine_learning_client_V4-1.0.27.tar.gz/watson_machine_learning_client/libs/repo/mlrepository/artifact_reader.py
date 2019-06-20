################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################


class ArtifactReader(object):
    """
    Template reader class used to read artifacts.
    """

    def read(self):
        """
        Returns stream object with content of pipeline/pipeline model.

        :return: binary stream
        """
        pass

    def close(self):
        """
        Closes stream to content.
        """
        pass
