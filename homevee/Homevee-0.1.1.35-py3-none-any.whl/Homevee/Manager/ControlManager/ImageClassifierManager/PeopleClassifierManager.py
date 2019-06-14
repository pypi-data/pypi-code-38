from Homevee.AIAgents.ImageClassifier.PeopleClassifier import PeopleClassifier
from Homevee.AIAgents.ImageClassifierRetrainer.PeopleClassifierRetrainer import PeopleClassifierRetrainer
from Homevee.Manager.ControlManager.ImageClassifierManager import ImageClassifierManager


class PeopleClassifierManager(ImageClassifierManager):
    def __init__(self):
        data_table = "PEOPLE_DATA"
        learning_data_table = "PEOPLE_LEARNING_DATA"
        settings_prefix = "AR_"

        classifier = PeopleClassifier()
        retrainer = PeopleClassifierRetrainer()

        is_training_tag = "PEOPLE_CLASSIFIER_TRAINING_RUNNING"
        classifier_tag = "people"

        super(PeopleClassifierManager, self).__init__(data_table=data_table, learning_data_table=learning_data_table,
                                                      settings_prefix=settings_prefix, is_training_tag=is_training_tag,
                                                      classifier_tag=classifier_tag, classifier=classifier, retrainer=retrainer)
        return