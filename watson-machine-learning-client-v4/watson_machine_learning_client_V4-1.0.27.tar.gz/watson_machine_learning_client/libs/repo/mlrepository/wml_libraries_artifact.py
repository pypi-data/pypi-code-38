################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################


from .artifact import Artifact


class WmlLibrariesArtifact(Artifact):
    """
    Class representing WmlLibraryArtifact artifact.

    :param str uid: optional, uid which indicate that artifact already exists in repository service
    :param str name: optional, name of artifact
    :param MetaProps meta_props: optional, props used by other services
    """
    def __init__(self, uid, name, meta_props):
        super(WmlLibrariesArtifact, self).__init__(uid, None, meta_props)
