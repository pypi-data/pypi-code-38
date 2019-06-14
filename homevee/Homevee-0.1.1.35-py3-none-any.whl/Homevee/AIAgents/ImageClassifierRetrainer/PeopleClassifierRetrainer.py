from Homevee.AIAgents.ImageClassifierRetrainer import ImageClassifierRetrainer


class PeopleClassifierRetrainer(ImageClassifierRetrainer):
    def __init__(self):
        image_dir_name = "people_classifier"
        model_dir_name = "people_temp"
        retrainer_name = "Personenerkennung"
        super(PeopleClassifierRetrainer, self).__init__(image_dir_name, model_dir_name, retrainer_name)