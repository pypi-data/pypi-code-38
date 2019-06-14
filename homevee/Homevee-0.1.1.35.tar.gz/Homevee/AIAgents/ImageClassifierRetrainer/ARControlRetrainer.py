from Homevee.AIAgents.ImageClassifierRetrainer import ImageClassifierRetrainer


class ARControlRetrainer(ImageClassifierRetrainer):
    def __init__(self):
        image_dir_name = "ar_control"
        model_dir_name = "ar_control_temp"
        retrainer_name = "AR-Control"
        super(ARControlRetrainer, self).__init__(image_dir_name, model_dir_name, retrainer_name)