import sys
import basis_set_exchange as bse
import datetime

md = bse.get_metadata()

for bs,v in md.items():
    if '1' in v['versions']:
        for ver,verdata in v['versions'].items():
            if ver == '0':
                continue
            table_file = verdata['file_relpath']
            print(table_file)
            #a = bse.fileio.read_json_basis(table_file)
            #a['revision_date'] = dt.strftime('%Y-%m-%d')
            #bse.fileio.write_json_basis(table_file, a)
