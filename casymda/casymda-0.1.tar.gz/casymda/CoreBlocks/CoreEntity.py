# has environment and name
# to be moved between components, remembering it's last time of arrival
# can seize resources (corresponding requests are stored in list)


class CoreEntity:
    def __init__(self, env, name):
        self.env = env
        self.name = name

        self.seizedResources = []  # requested resources, info needed for release
        self.timeOfArrival = None
