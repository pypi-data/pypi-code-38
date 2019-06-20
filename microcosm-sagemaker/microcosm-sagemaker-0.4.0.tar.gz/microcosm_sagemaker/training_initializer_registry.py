class TrainingInitializerRegistry:
    """
    The training initializer registry is a place to register functions that need to be
    called during training initialization.  A typical example of this is to
    seed random number generators.

    """
    def __init__(self, graph):
        self.graph = graph
        self.initializers = []

    def register(self, initializer):
        self.initializers.append(initializer)

    def init(self):
        for initializer in self.initializers:
            initializer.init()
