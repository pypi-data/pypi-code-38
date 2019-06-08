import sys
import basis_set_exchange as bse
import pandas as pd
import datetime
import pytz

md = bse.get_metadata()

bse_map = {
   'dzp': 'jorge-dzp', 
   'tzp': 'jorge-tzp', 
   'qzp': 'jorge-tzp', 
   '5zp': 'jorge-tzp', 
   '6zp': 'jorge-tzp', 
   'dzp-dkh': 'jorge-dzp-dkh', 
   'tzp-dkh': 'jorge-tzp-dkh', 
   'qzp-dkh': 'jorge-tzp-dkh', 
   '5zp-dkh': 'jorge-tzp-dkh', 
   '6zp-dkh': 'jorge-tzp-dkh',
   'modified lanl2dz': 'modified-lanl2dz',
   'x2c-coulomb-fitting': 'x2c-jfit',
   'sbkjc ecp': 'sbkjc-ecp',
   'sbkjc vdz ecp': 'sbkjc-vdz'
}


for bs,v in md.items():
    for ver,verdata in v['versions'].items():
        table_file = verdata['file_relpath']
        a = bse.fileio.read_json_basis(table_file)
        if not 'revision_date' in a:
            print('{:22}  {}'.format(bs, ver))
