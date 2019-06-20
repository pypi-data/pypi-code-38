################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################


from watson_machine_learning_client.libs.repo.mlrepository import MetaNames, MetaProps, WmlExperimentArtifact
from watson_machine_learning_client.libs.repo.util.exceptions import MetaPropMissingError


class ExperimentArtifact(WmlExperimentArtifact):
    """
    Class of Experiment artifacts created with MLRepositoryCLient.

    """
    def __init__(self,  uid=None, name=None, meta_props=MetaProps({})):
        super(ExperimentArtifact, self).__init__(uid, name, meta_props)


        if meta_props.prop(MetaNames.EXPERIMENTS.PATCH_INPUT) is None:
            if meta_props.prop(MetaNames.EXPERIMENTS.SETTINGS) is None :
                 raise MetaPropMissingError('Value specified for "meta_props" does not contain value for '
                                         '"MetaNames.EXPERIMENTS.SETTINGS"')

            if meta_props.prop(MetaNames.EXPERIMENTS.TRAINING_REFERENCES) is None :
                raise MetaPropMissingError('Value specified for "meta_props" does not contain value for '
                                       '"MetaNames.EXPERIMENTS.TRAINING_REFERENCES"')

            if meta_props.prop(MetaNames.EXPERIMENTS.TRAINING_DATA_REFERENCE) is None :
                raise MetaPropMissingError('Value specified for "meta_props" does not contain value for '
                                       '"MetaNames.EXPERIMENTS.TRAINING_DATA_REFERENCE"')


