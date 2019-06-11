class StartupTrigger:
    def __init__(self, action):
        action()

    def unregister(self):
        pass


triggers = {'on eeve startup': StartupTrigger}
