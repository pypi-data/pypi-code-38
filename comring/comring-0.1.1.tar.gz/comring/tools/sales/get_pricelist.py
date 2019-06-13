from comring.lib import odoo
from comring.lib import config
import getpass
import logging
import csv

env = 'live'
out_file = '/tmp/data_pricelist.csv'

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

conf = config.Config()

url = conf.env_get(env, 'server_url')
db = conf.env_get(env, 'database')
user = conf.env_get(env, 'user')

logging.info('Logging in to %s database [%s] as [%s]', url, db, user)
passwd = ''
try:
    passwd = getpass.getpass(prompt='Password for {}: '.format(user))
except Exception as err:
    logging.error('ERROR while getting password', exc_info=err)
    exit(1)

osv = odoo.Odoo(url)
try:
    client = osv.login(db, user, passwd)
except Exception as err:
    logging.error('ERROR while logging in', exc_info=err)
    exit(2)


def get_data(client, prod_ids, pricelist_id):
    data = client.read('product.product', prod_ids,
                       ['id', 'default_code', 'name', 'price'],
                       context={'pricelist': pricelist_id}
                       )
    return data


product_ids = client.search('product.product', [['sale_ok', '=', True]])
logging.debug('Got %d products to get', len(product_ids))

data_gt = get_data(client, product_ids, 1)
data_mt = get_data(client, product_ids, 2280)

merged = []
merged_index = {}
for d in data_gt:
    merged_index[d['id']] = len(merged)
    merged.append({
        'id': d['id'],
        'default_code': d['default_code'],
        'name': d['name'],
        'price_gt': d['price']
    })

for d in data_mt:
    idx = merged_index[d['id']]
    merged[idx]['price_mt'] = d['price']


logging.info('Writing %d rows of data to %s', len(merged), out_file)
with open(out_file, 'wt') as f:
    w = csv.DictWriter(f, merged[0].keys())
    w.writeheader()
    for m in merged:
        w.writerow(m)

logging.info('Done')
