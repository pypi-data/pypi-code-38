from lxml import etree
import pygsheets
import pandas as pd

gc = pygsheets.authorize(service_file='E:\projekti na lokalnom\project for testing\get_guids_for_profiles\clsc.json', no_cache=True)
df = pd.DataFrame()
df['name'] = ['John', 'Steve', 'Sarah']
sh = gc.open_by_url('https://docs.google.com/spreadsheets/d/14ep2SnXs12CT937L4LZAeTqlc8e8TWo34NpFGclWsr0/edit#gid=400628164')
wks = sh[0]

# sh.add_worksheet('new data sheet', wks)
print('stop')