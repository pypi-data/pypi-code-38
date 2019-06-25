import os
from csv import DictReader

dir_path = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(dir_path, 'db', 'cae2scian.tsv')
db = dict(
  [
    (r['cae_id'], dict(r)) for r in DictReader(open(db_path), delimiter='\t')
  ]
)

def cae(industry_code):
  return db[industry_code]
