from simpy import Resource


# extends basic simpy resource by name property

class CoreResource(Resource):
    def __init__(self, env, name, capacity=1, xy=None, ways=None):
        super().__init__(env, capacity=capacity)

        self.name = name
