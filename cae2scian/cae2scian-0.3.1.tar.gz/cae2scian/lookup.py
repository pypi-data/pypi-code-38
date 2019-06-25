import os
from csv import DictReader

dir_path = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(dir_path, 'db', 'cae2scian.tsv')

class CAE(object):
  def __init__(self):
    _ = dict()
    for row in DictReader(open(db_path), delimiter='\t'):
      _.setdefault(row['cae_id'], []).append({
          "code_scheme_id": "ca_naics_2017",
          "code": row['scian_id'],
          "name": row['scian_title_fr']
        })
    self.db = _

  def lookup(self, cae_id):
    return self.db.get(cae_id)
