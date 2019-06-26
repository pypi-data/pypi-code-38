from algonaut.settings import settings
"""
This is the module that should be loaded by celerybeat
and celeryd. It will make sure to first initialize
the settings before generating the application object.
"""


#we initialize the settings
settings.initialize()
#we make the application object available
app = settings.celery
