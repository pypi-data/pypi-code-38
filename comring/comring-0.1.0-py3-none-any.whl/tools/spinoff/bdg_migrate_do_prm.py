import logging
import os
import io
import csv
from comring.lib import odoo, cache

class ProductCache(object):
    def __init__(self):
        self._data = []
        self._fields = ['id', 'name', 'default_code', 'uom_id', 'taxes_id', 'supplier_taxes_id', 'tags', 'categ_id', 'price']

    def prefetch_by_id(self, client, ids, context=None):
        self._data = client.read('product.product',
                                 ids,
                                 self._fields,
                                 context
                                 )

    def prefetch_by_code(self, client, product_codes, context=None):
        self._data = client.search_read('product.product',
                                        [['default_code', 'in', product_codes]],
                                        self._fields,
                                        context
                                        )

    def get_with_id(self, prod_id):
        res = None
        for d in self._data:
            if d['id'] == prod_id:
                res = d
                break
        return res

    def get_with_code(self, prod_code):
        res = None
        for d in self._data:
            if d['default_code'] == prod_code:
                res = d
                break
        return res

def load_picking_numbers(filename):
    rows = []
    with io.open(filename, 'rt') as f:
        reader = csv.DictReader(f, delimiter=',', quotechar='"')
        for row in reader:
            rows.append(row)
    return rows

def read_partner_by_code(client, partner_code, fields):
    partners = client.search_read('res.partner', [['ref', '=', partner_code]], fields)
    if partners and len(partners) > 0:
        return partners[0]
    return None

#------------------------------------------------------------------------
# LIVE - Read DO Data
#
def create_source_do_data(client, do_numbers):
    result = []
    pickings = client.search_read('stock.picking',
                                  [['name', 'in', do_numbers]],
                                  ['id', 'name', 'partner_id',
                                   'pack_operation_product_ids'
                                   ]
                                  )

    all_pack_op_ids = []
    for picking in pickings:
        all_pack_op_ids += picking['pack_operation_product_ids']
    picking_operation_cache = cache.SimpleCache(client, 'stock.pack.operation',
                                                [
                                                    'id', 'product_id', 'qty_done'
                                                ],
                                                'id')
    picking_operation_cache.prefetch(all_pack_op_ids)
    all_product_ids = set([x['product_id'][0] for x in picking_operation_cache])
    product_cache = cache.SimpleCache(client, 'product.product',
                                      ['id', 'default_code'], 'id')
    for picking in pickings:
        if not picking['partner_id']:
            raise ValueError('Undefined partner in picking {}'.format(picking['number']))
        partner = client.read_one('res.partner', picking['partner_id'][0],
                                  ['id', 'name', 'ref'])
        do = {
            'name': picking['name'],
            'partner_code': partner['ref'],
            'lines': []
        }
        for op_id in picking['pack_operation_product_ids']:
            pack_op = picking_operation_cache.read(op_id)
            line = {
                'product_code': product_cache.read(pack_op['product_id'][0])['default_code'],
                'quantity': pack_op['qty_done']
            }
            do['lines'].append(line)

        result.append(do)

    return result

#------------------------------------------------------------------------
# LIVE - Create PRM SO
def create_prm_so_data(client, product_by_qty, do_number_list):
    parama_partner_id = client.search('res.partner', [['ref', '=', '110644-000']])
    if not parama_partner_id:
        raise Exception('Could not get ID for Parama')

    dc_bandung_id = client.search('res.partner', [['ref', '=', 'D04']])
    if not dc_bandung_id:
        raise Exception('Could not get ID for DC Bandung')

    sales_id = client.search('res.partner', [['ref', '=', '303213']])
    if not sales_id:
        raise Exception('Could not get ID for salesperson (Andini)')

    order_method_id = client.search('order.method', [['name', '=', 'Salesperson']])
    if not order_method_id:
        raise Exception('Could not get ID for order method')

    warehouse_id = client.search('stock.warehouse', [['code', '=', 'PD04']])
    if not warehouse_id:
        raise Exception('Could not get ID for warehouse')

    so = {
        'partner_id': parama_partner_id[0],
        'dc_id': dc_bandung_id[0],
        'sales_id': sales_id[0],
        'client_order_ref': 'Outstanding DO Migrasi Spinoff Bandung',
        'order_method': order_method_id[0],
        'warehouse_id': warehouse_id[0],
        'date_order': '2018-01-31',
        'pricelist_id': 1,
        'origin': ', '.join(do_number_list),
        'allow_finance': True
    }

    logging.debug('Caching product data')
    product_codes = list(product_by_qty.keys())
    cats = {}
    product_data = client.search_read(
        'product.product',
        [['default_code', 'in', product_codes]],
        ['id', 'name', 'default_code', 'uom_id', 'taxes_id', 'price'],
        {'pricelist': so['pricelist_id']}
    )
    # for pd in product_data:
    #     cat_key = pd['categ_id'][1]
    #     if cat_key not in cats:
    #         cats[cat_key] = 1
    #     else:
    #         cats[cat_key] += 1

    # for cat in cats:
    #     logging.debug('Category %s: %d', cat, cats[cat])

    so['order_line'] = []
    for prod_qty_key in product_by_qty:
        pd = None
        for pdl in product_data:
            if str(pdl['default_code']) == prod_qty_key:
                pd = pdl
                break

        so_line = {
            'name': pd['name'],
            'product_id': pd['id'],
            'product_uom': pd['uom_id'][0],
            'product_uom_qty': product_by_qty[prod_qty_key],
            'price_unit_hidden': pd['price'],
            'tax_id': [(4, pd['taxes_id'][0], 0)],
            'editable_price': True
        }
        so['order_line'].append((0, 0, so_line))

    return so

#------------------------------------------------------------------------
# SPINOFF - Create Paragon Invoice
#
def create_spinoff_invoice_data(client, product_by_qty, do_number_list):
    company_id = client.search('res.company', [['name', '=', 'PT PARAGON TECHNOLOGY AND INNOVATION']])
    if not company_id:
        raise Exception('Could not get ID for company Paragon')

    parama_partner_id = client.search('res.partner', [['ref', '=', '110644-000']])
    if not parama_partner_id:
        raise Exception('Could not get ID for Parama')

    dc_bandung_id = client.search('res.partner', [['ref', '=', 'D04']])
    if not dc_bandung_id:
        raise Exception('Could not get ID for DC Bandung')

    sales_id = client.search('res.partner', [['ref', '=', '303213']])
    if not sales_id:
        raise Exception('Could not get ID for salesperson (Andini)')

    payment_term_id = client.search('account.payment.term', [['name', '=', '30 Net Days']])
    if not payment_term_id:
        raise Exception('Could not get ID for payment term')

    journal_id = client.search('account.journal', [['name', '=', 'Normal Sales Paragon']])
    if not journal_id:
        raise Exception('Could not get ID for journal')

    sale_account_id = client.search('account.account', [['code', '=', '410101001']])
    if not sale_account_id:
        raise Exception('Could not get ID for sale account')

    discount_ids = client.read('res.partner', [parama_partner_id[0]], ['discount_customer'])
    discount_ids = discount_ids[0]['discount_customer']
    discounts = client.read('discount.discount', discount_ids, ['id', 'name', 'tags'])

    inv = {
        'partner_id': parama_partner_id[0],
        'dc_id': dc_bandung_id[0],
        'payment_term_id': payment_term_id[0],
        'type_code_invoice': '10',
        'journal_id': journal_id[0],
        'origin': ', '.join(do_number_list),
        'date_invoice': '2018-02-01',
        'shipping_date': '2018-02-01',
        'date_posted': '2018-02-01',
        'pkp': True,
        'type': 'out_invoice',
        'company_id': company_id[0]
    }

    product_codes = list(product_by_qty.keys())
    pcache = ProductCache()
    pcache.prefetch_by_code(client, product_codes, {'pricelist': 1})

    inv['invoice_line_ids'] = []
    for prod_code in product_by_qty:
        prod = pcache.get_with_code(prod_code)
        if not prod:
            raise Exception('Product not found in cache: {}'.format(prod_code))
        line = {
            'product_id': prod['id'],
            'account_id': sale_account_id[0],
            'name': prod['name'],
            'price_unit': prod['price'],
            'quantity': product_by_qty[prod_code],
            'uom_id': prod['uom_id'][0],
            'invoice_line_tax_ids': [[4, prod['taxes_id'][0], 0]]
        }
        line_discounts = []
        for disc in discounts:
            for tag_id in prod['tags']:
                if disc['tags'][0] == tag_id:
                    line_discounts.append((4, disc['id'], 0))
        if line_discounts:
            line['discount_m2m'] = line_discounts
        inv['invoice_line_ids'].append((0, 0, line))

    return inv

#------------------------------------------------------------------------
# SPINOFF - Create Parama Vendor bill
#
def create_spinoff_vbill_data(client, product_by_qty, do_number_list):
    company_id = client.search('res.company', [['name', '=', 'PT PARAMA GLOBAL INSPIRA']])
    if not company_id:
        raise Exception('Could not get ID for company Parama')

    partner_id = client.search('res.partner', [['ref', '=', '114953-000']])
    if not partner_id:
        raise Exception('Could not get ID for Paragon')

    dc_bandung_id = client.search('res.partner', [['ref', '=', 'D04']])
    if not dc_bandung_id:
        raise Exception('Could not get ID for DC Bandung')

    # sales_id = client.search('res.partner', [['ref', '=', '303213']])
    # if not sales_id:
    #     raise Exception('Could not get ID for salesperson (Andini)')

    payment_term_id = client.search('account.payment.term', [['name', '=', '45 Net Days']])
    if not payment_term_id:
        raise Exception('Could not get ID for payment term')

    journal_id = client.search('account.journal', [['name', '=', 'Vendor bill parama']])
    if not journal_id:
        raise Exception('Could not get ID for journal')

    account_id = client.search('account.account', [['code', '=', '2102001001']])
    if not account_id:
        raise Exception('Could not get ID for account')

    discount_ids = client.read('res.partner', [partner_id[0]], ['discount_customer'])
    discount_ids = discount_ids[0]['discount_customer']
    discounts = client.read('discount.discount', discount_ids, ['id', 'name', 'tags'])

    inv = {
        'partner_id': partner_id[0],
        'dc_id': dc_bandung_id[0],
        'payment_term_id': payment_term_id[0],
        'type_code_invoice': '10',
        'journal_id': journal_id[0],
        'origin': ', '.join(do_number_list),
        'date_invoice': '2018-02-01',
        'shipping_date': '2018-02-01',
        'date_posted': '2018-02-01',
        'pkp': True,
        'type': 'in_invoice',
        'company_id': company_id[0]
    }

    product_codes = list(product_by_qty.keys())
    pcache = ProductCache()
    pcache.prefetch_by_code(client, product_codes, {'pricelist': 1})

    inv['invoice_line_ids'] = []
    for prod_code in product_by_qty:
        prod = pcache.get_with_code(prod_code)
        line = {
            'product_id': prod['id'],
            'account_id': account_id[0],
            'name': prod['name'],
            'price_unit': prod['price'],
            'quantity': product_by_qty[prod_code],
            'uom_id': prod['uom_id'][0],
            'invoice_line_tax_ids': [[4, prod['supplier_taxes_id'][0], 0]]
        }
        line_discounts = []
        for disc in discounts:
            for tag_id in prod['tags']:
                if disc['tags'][0] == tag_id:
                    line_discounts.append((4, disc['id'], 0))
        if line_discounts:
            line['discount_m2m'] = line_discounts
        inv['invoice_line_ids'].append((0, 0, line))

    return inv

#------------------------------------------------------------------------
# SPINOFF - Create Parama Invoices to Customer
#
def create_spinoff_parama_customer_invoices(client, do_list):
    result = []
    company_id = client.search_one('res.company',
                                   [['name', '=', 'PT PARAMA GLOBAL INSPIRA']])
    dc_id = client.search_one('res.partner', [['ref', '=', 'D04']])
    journal_id = client.search_one('account.journal', [['name', '=', 'Normal Sales Parama']])
    line_account_id = client.search_one('account.account', [['code', '=', '4101001001']])
    for do_data in do_list:
        inv = {}
        partner = client.search_read_one('res.partner',
                                         [['ref', '=', do_data['partner_code']]],
                                         ['id', 'name', 'property_product_pricelist', 'pkp',
                                          'property_payment_term_id',
                                          'property_account_receivable_id',
                                          'discount_customer'
                                         ]
        )
        inv['partner_id'] = partner['id']
        inv['company_id'] = company_id
        inv['dc_id'] = dc_id
        inv['payment_term_id'] = partner['property_payment_term_id'][0]
        inv['type_code_invoice'] = '10'
        inv['journal_id'] = journal_id
        inv['origin'] = do_data['name']
        inv['date_invoice'] = '2018-02-01'
        inv['shipping_date'] = '2018-02-01'
        inv['date_posted'] = '2018-02-01'
        inv['pkp'] = partner['pkp']
        inv['type'] = 'out_invoice'
        inv['invoice_line_ids'] = []

        product_codes_unique = list(set([x['product_code'] for x in do_data['lines']]))
        product_cache = cache.SimpleCache(client, 'product.product',
                                          [
                                              'id', 'name', 'default_code',
                                              'price', 'uom_id', 'taxes_id',
                                              'tags'
                                          ], 'default_code')

        product_data = client.search_read('product.product',
                                          [['default_code', 'in', product_codes_unique]],
                                          [
                                              'id', 'name', 'default_code',
                                              'price', 'uom_id', 'taxes_id',
                                              'tags'
                                          ],
                                          context={
                                              'pricelist': partner['property_product_pricelist'][0]
                                          }
                                          )
        product_data_dict = {}
        for prod in product_data:
            product_data_dict[prod['default_code']] = prod

        discounts = []
        if partner['discount_customer']:
            discounts = client.read('discount.discount', partner['discount_customer'],
                                    ['id', 'name', 'tags'])
        for line in do_data['lines']:
            product = product_data_dict[line['product_code']]
            inv_line = {
                'product_id': product['id'],
                'account_id': line_account_id,
                'name': product['name'],
                'price_unit': product['price'],
                'quantity': line['quantity'],
                'uom_id': product['uom_id'][0],
                'invoice_line_tax_ids': [[4, product['taxes_id'][0], 0]]
            }

            line_discount = []
            for disc in discounts:
                for prod_tag in product['tags']:
                    if disc['tags'][0] == prod_tag:
                        line_discount.append([4, disc['id'], 0])
            if line_discount:
                inv_line['discount_m2m'] = line_discount

            inv['invoice_line_ids'].append([0, 0, inv_line])

        result.append(inv)

    return result


#------------------------------------------------------------------------
# Creation functions
#
def create_live_so(client, so_data):
    logging.info('Create SO in target server')
    so_id = client.create('sale.order', so_data)
    if not so_id:
        logging.error('Error while creating sales order')
        return False
    so = client.read('sale.order', [so_id], ['id', 'name'])
    if so:
        logging.info('SO created: %s', so[0]['name'])

    return so

def create_spinoff_invoice(client, inv_data):
    logging.info('Create Draft Paragon Invoice in Spinoff server')
    inv_id = client.create('account.invoice', inv_data)
    if not inv_id:
        logging.error('Error while creating invoice')
        return False
    logging.info('Invoice created: %d', inv_id)
    return inv_id

def create_spinoff_vbill(client, bill_data):
    logging.info('Create Draft Parama Vendor Bill in Spinoff server')
    bill_id = client.create('account.invoice', bill_data)
    if not bill_id:
        logging.error('Error while creating vendor bill')
        return False
    logging.info('Vendor bill created: %d', bill_id)
    return bill_id

def create_spinoff_customer_invoice(client, invoices):
    logging.info('Create Parama Invoice to Customer in Spinoff server')
    for inv in invoices:
        inv_id = client.create('account.invoice', inv)
        logging.info('Invoice created: %d', inv_id)
        inv['id'] = inv_id
    return invoices

#------------------------------------------------------------------------
# Main
#
def main():
    osv = odoo.Odoo('https://odoo.pti-cosmetics.com')
    client = osv.login('paragon', 'it-agustianes', 'amidis 1234')
    if not client:
        logging.error('Could not connect to source server')
        return False

    osv_target = odoo.Odoo('https://odoo.pti-cosmetics.com')
    client_target = osv_target.login('paragon', 'it-agustianes', 'amidis 1234')
    if not client_target:
        logging.error('Could not connect to target server')
        return False

    osv_spinoff = odoo.Odoo('https://erp.pti-cosmetics.com')
    client_spinoff_pti = osv_spinoff.login('spinoff', 'support-anes', '1')
    client_spinoff_prm = osv_spinoff.login('spinoff', 'admin.parama@email.com', '*&hGQ54X')
    if not client_spinoff_pti:
        logging.error('Could not connect to spinoff server Paragon')
        return False
    if not client_spinoff_prm:
        logging.error('Could not connect to spinoff server Parama')
        return False

    filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'bdg_migrate_picking-cons.csv')
    picking_input = load_picking_numbers(filename)
    picking_numbers = list(map(lambda x: x['number'], picking_input))

    logging.info('Reading data from source server')
    do_list = create_source_do_data(client, picking_numbers)

    product_qty_by_code = {}
    for do in do_list:
        for line in do['lines']:
            pcode = line['product_code']
            if pcode in product_qty_by_code:
                product_qty_by_code[pcode] += line['quantity']
            else:
                product_qty_by_code[pcode] = line['quantity']


    # logging.info('Constructing SO Data')
    # so_data = create_prm_so_data(client_target, product_qty_by_code, picking_numbers)
    # so = create_live_so(client_target, so_data)

    # logging.info('Constructing Invoice Data')
    # inv_data = create_spinoff_invoice_data(client_spinoff_pti, product_qty_by_code, picking_numbers)
    # inv_id = create_spinoff_invoice(client_spinoff_pti, inv_data)

    # logging.info('Constructing Vendor Bill Data')
    # bill_data = create_spinoff_vbill_data(client_spinoff_prm, product_qty_by_code, picking_numbers)
    # bill_id = create_spinoff_vbill(client_spinoff_prm, bill_data)

    logging.info('Construction Parama Customer Invoice Data')
    cust_inv_data = create_spinoff_parama_customer_invoices(client_spinoff_prm, do_list)
    cust_inv_ids = create_spinoff_customer_invoice(client_spinoff_prm, cust_inv_data)

    return True


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
    main()
