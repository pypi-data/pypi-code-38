from django.core.management.base import BaseCommand

# from meteo.pgutils import load_data
from measurements.settings import SOURCE_AUTH
from measurements.sources.pessl import PesslAPI
from measurements.sources.mtt import MttAPI
from measurements.models import SourceType, Measure

a = MttAPI()
a.get_df(code='T0193')


from psqlextra.query import ConflictAction


ps = SourceType.objects.get(code='pessl')
for s in ps.station_set.all():
    keys = SOURCE_AUTH['pessl'][s.network.code]
    print(keys)
    pesslapi = PesslAPI(keys['public_key'],
                            keys['private_key'])
    df = pesslapi.get_df(s.code, 1000)
    print(df)



a = df[['HC Air temperature|avg']].copy()
a.reset_index(inplace=True)
a.columns = ['timestamp', 'value']
a['serie_id'] = 2

Measure.extra.on_conflict(['serie_id', 'timestamp', 'value'],
                          ConflictAction.UPDATE).bulk_insert(
    a.to_dict(orient='record'))

from measurements.sources.davis import DavisAPI

ds = DavisAPI()
a = ds.get_df('cantineferrari/ferrari1')


from django.conf import settings
from measurements.sources.elmed import ElmedAPI
elmed = ElmedAPI(None, settings.MEASUREMENTS_SOURCE_AUTH['elmed']['ferrari']['private_key'])
df = elmed.get_df(88)