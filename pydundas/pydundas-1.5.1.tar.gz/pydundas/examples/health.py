from pydundas import Api, Session, creds_from_yaml
import sys
import json
creds = creds_from_yaml('credentials.yaml')

d = Session(**creds, loglevel='debug')
d.login()
api = Api(d)
hapi = api.health()

hapi.check(allchecks=True)
# Delete old unused tables
hapi.fix(['DBI2000'])
