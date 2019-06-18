from .initializer_model import InitializerModel


class UserStories(InitializerModel):

    def __init__(self, stories=[], owner=None):
        super().__init__()
        if stories is None:
            stories = []
        self.owner = owner
        self.stories = stories
