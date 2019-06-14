from Homevee.AIAgents.ImageClassifier import ImageClassifier


class PeopleClassifier(ImageClassifier):
    def __init__(self):
        model_name = "people_temp"
        super(PeopleClassifier, self).__init__(model_name)
        return