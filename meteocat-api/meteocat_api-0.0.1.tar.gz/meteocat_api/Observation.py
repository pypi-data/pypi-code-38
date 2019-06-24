import datetime

class Observation(object):
    def __init__(self, api_key=""):
        self.api_key = api_key

        self.date = None
        self.name = None
        self.longitude = None
        self.latitude = None
        self.id = None
        self.elevation = None
        
        # Stores a list of observations in days
        self.timesteps = []

    def now(self):
        """
        Return the final timestep available. This is the most recent observation.
        """

        return self.timesteps[-1]
