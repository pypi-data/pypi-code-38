class NlpPipeline(TextPreprocessing):

    def __init__(self, strategy):

        super(NlpPipeline, self).__init__()
        self.strategy = strategy

        assert isinstance(self.strategy, list), "Please pass a list of possible operations"

    def get_operations(self):
        return dir(TextPreprocessing)