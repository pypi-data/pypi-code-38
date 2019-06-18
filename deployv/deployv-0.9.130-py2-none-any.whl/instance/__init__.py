from collections import defaultdict

ODOO_BINARY = defaultdict(lambda: 'odoo-bin',
                          {
                              '7.0': 'openerp-server',
                              '8.0': 'odoo.py',
                              '9.0': 'odoo.py',
                              '10.0': 'odoo-bin',
                              'saas-14': 'odoo-bin',
                              'saas-15': 'odoo-bin',
                          })

SAAS_VERSIONS = {
    'saas-14': 'saas-14',
    'saas-15': 'saas-15',
    'saas-17': 'saas-17',
}
