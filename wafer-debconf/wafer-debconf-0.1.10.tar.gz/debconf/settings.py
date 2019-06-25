from wafer.settings import *

TEMPLATES[0]['OPTIONS']['context_processors'] += ('debconf.context_processors.expose_time_zone',)
