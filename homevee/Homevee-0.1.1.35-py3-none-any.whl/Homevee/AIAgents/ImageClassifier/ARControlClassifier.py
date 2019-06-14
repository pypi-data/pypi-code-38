from Homevee.AIAgents.ImageClassifier import ImageClassifier


class ARControlClassifier(ImageClassifier):
    def __init__(self):
        model_name = "ar_control_temp"
        super(ARControlClassifier, self).__init__(model_name)
        return