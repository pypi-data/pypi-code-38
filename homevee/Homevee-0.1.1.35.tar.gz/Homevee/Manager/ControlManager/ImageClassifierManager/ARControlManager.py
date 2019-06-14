from Homevee.AIAgents.ImageClassifier.ARControlClassifier import ARControlClassifier
from Homevee.AIAgents.ImageClassifierRetrainer.ARControlRetrainer import ARControlRetrainer
from Homevee.Manager.ControlManager.ImageClassifierManager import ImageClassifierManager


class ARControlManager(ImageClassifierManager):
    def __init__(self):
        data_table = "AR_CONTROL_CLASSES"
        learning_data_table = "AR_CONTROL_LEARNING_DATA"
        settings_prefix = "PEOPLE_"

        classifier = ARControlClassifier()
        retrainer = ARControlRetrainer()

        is_training_tag = "AR_CONTROL_TRAINING_RUNNING"
        classifier_tag = "arcontrol"

        super(ARControlManager, self).__init__(data_table=data_table, learning_data_table=learning_data_table,
                                                      settings_prefix=settings_prefix, is_training_tag=is_training_tag,
                                                      classifier_tag=classifier_tag, classifier=classifier, retrainer=retrainer)
        return