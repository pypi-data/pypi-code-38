
class BaseBuilder(object):

    """
    A builder generates content for the site in two phases:

    * Indexing (to generate links and structures that can be used by other builders)
    * Building (where the actual content is being generated)
    * Post-Processing (where additional work can be performed)
    """

    def index(self, params, language):
        return {}

    def build(self):
        pass

    def postprocess(self):
        pass

    def __init__(self, site):
        self.site = site
        self.providers = {}
        self.addons = {}

    