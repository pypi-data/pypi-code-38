from .initializer_model import InitializerModel

class UserStories(InitializerModel):
    def __init__(self,owner = None, stories = []):
        self.owner = owner
        self.stories = stories