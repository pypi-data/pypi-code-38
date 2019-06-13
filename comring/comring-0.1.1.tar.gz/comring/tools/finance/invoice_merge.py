from comring.lib import tool
import logging

LOGGER = logging.getLogger(__name__)

class ProductCache(object):
    def __init__(self, client):
        self.client = client
        self.by_id = {}
        self.by_code = {}

    def read_from_odoo(self, domain):
        prods = self.client.search_read('product.product', domain, ['id', 'default_code', 'name', 'product_tmpl_id', 'property_account_income_id', 'property_account_income_id'])
        for prod in prods:
            self.by_id[prod['id']] = prod
            self.by_code[prod['default_code']] = prod

    def precache(self):
        self.read_from_odoo(self, [['code', '!=', False]])

    def read_ids(self, prod_ids):
        cached_ids = set(self.by_id.keys())
        requested_ids = set(prod_ids)
        to_fetch = list(requested_ids.difference(cached_ids))
        if len(to_fetch) > 0:
            self.read_from_odoo([['id', 'in', to_fetch]])

    def get_by_id(self, prod_id):
        res = self.by_id.get(prod_id, None)
        if not res:
            self.read_from_odoo([['id', '=', prod_id]])
            res = self.by_id.get(prod_id, None)
        return res

    def get_by_code(self, prod_code):
        res = self.by_code.get(prod_code, None)
        if not res:
            self.read_from_odoo([['default_code', '=', prod_code]])
            res = self.by_code.get(prod_code, None)
        return res
        
class InvMerge(tool.SimpleTool):
    
    def __init__(self):
        super().__init__()
        self.so_domain = []
        self.inv_ref = ''
        self.journal_code = ''
        self.type_code = ''
        self.product_cache = None

    def connect(self):
        super().connect()
        self.product_cache = ProductCache(self._client)

    def boot_add_arguments(self, parser):
        super().boot_add_arguments(parser)
        parser.add_argument('-r', '--reference', help='Provide invoice reference/description', type=str, default='')
        parser.add_argument('-t', '--type', choices=['number', 'clientref'], help='Search type', required=True)
        parser.add_argument('-j', '--journal', choices=['PTI50', 'PRM50', 'PTI51', 'PRM51'], help='Journal code', required=True)
        parser.add_argument('-c', '--type-code', choices=['10', '20'], help='10=normal, 20=consignment', required=True)
        parser.add_argument('search', metavar='S', type=str, nargs='+', help='Search terms')

    def boot_process_arguments(self, args):
        super().boot_process_arguments(args)
        if args.type == 'number':
            self.so_domain.append(('name', 'in', args.search))
        if args.type == 'clientref':
            self.so_domain.append(('client_order_ref', 'in', args.search))
        self.so_domain.append(('state', '=', 'sale'))

        self.inv_ref = args.reference
        self.journal_code = args.journal
        self.type_code = args.type_code

    def merge_line(self, lines_by_hash, new_line):
        line_hash = '{}:{}'.format(new_line['product_id'], new_line['price_unit'])
        existing = lines_by_hash.get(line_hash, None)
        if not existing:
            lines_by_hash[line_hash] = new_line
        else:
            existing['quantity'] += new_line['quantity']
            if existing['origin']:
                existing['origin'] += ',' + new_line['origin']
            else:
                existing['origin'] = new_line['origin']

    def build_invoice_data(self):
        LOGGER.info('Building invoice data')
        inv_data = {}

        # Journal based on journal code
        LOGGER.info('Reading Journal data')
        journal_id = self.search('account.journal', [['code', '=', self.journal_code]], pos='one')
        if not journal_id:
            LOGGER.error('Journal with code %s not found', self.journal_code)
            return False
        inv_data['journal_id'] = journal_id

        # Read sales order data
        LOGGER.info('Reading sales order data')
        so_ids = self.search('sale.order', self.so_domain)
        if not so_ids or len(so_ids) < 1:
            LOGGER.error('No SO found')
            return False

        so_data = self.read('sale.order', so_ids, ['id', 'partner_invoice_id', 'name', 'client_order_ref', 'sales_id', 'fiscal_position_id', 'order_line', 'discount_lines'])

        # Read the partner based on the sales order and set it to invoice
        partner = self.read_one('res.partner', so_data[0]['partner_invoice_id'][0], ['id', 'name', 'property_account_receivable_id'])
        inv_data['partner_id'] = partner['id']

        # Set DC to Head Office
        dc_id = self.search('res.partner', [['is_dc', '=', True],['name', '=', 'HEAD OFFICE']], pos='one')
        inv_data['dc_id'] = dc_id

        # Fiscal position
        inv_data['fiscal_position_id'] = so_data[0]['fiscal_position_id'][0]

        # Read salesperson data and set it to invoice
        #salesperson = self.read_one('res.partner', so_data[0]['sales_id'][0], ['id', 'name'])
        #inv_data['sales_id'] = salesperson['id']

        # Set reference
        if self.inv_ref:
            inv_data['name'] = self.inv_ref
        else:
            inv_data['name'] = so_data[0]['client_order_ref']
        
        # Set account based on the partner
        inv_data['account_id'] = partner['property_account_receivable_id'][0]

        # Set invoice type
        inv_data['type_code_invoice'] = self.type_code
        inv_data['type'] = 'out_invoice'

        if len(so_data) <= 10:
            inv_data['origin'] = ', '.join(list(map((lambda so: so['name']), so_data)))
        else:
            inv_data['origin'] = 'SO CR:{} ({})'.format(inv_data['name'], len(so_data))

        # Create invoice lines
        LOGGER.info('Creating invoice lines data')
        lines_by_hash = {}
        inv_lines = []

        for so in so_data:
            logging.info(f"Creating lines for SO {so['name']}")
            sols = self.read('sale.order.line', so['order_line'], ['id', 'product_id', 'product_uom_qty', 'qty_delivered', 'qty_invoiced', 'product_uom', 'price_unit', 'tax_id', 'discount'])
            so_prod_ids = [sol['product_id'][0] for sol in sols]
            self.product_cache.read_ids(so_prod_ids)
            for so_line in sols:
                if so_line['qty_invoiced'] >= so_line['qty_delivered']:
                    continue
                product = self.product_cache.get_by_id(so_line['product_id'][0])
                taxes = [[6, 0, [ti]] for ti in so_line['tax_id']]
                line = {
                    'product_id': product['id'],
                    'name': product['name'],
                    'price_unit': so_line['price_unit'],
                    'quantity': so_line['product_uom_qty'],
                    'uom_id': so_line['product_uom'][0],
                    'discount': so_line['discount'],
                    'account_id': product['property_account_income_id'][0],
                    'invoice_line_tax_ids': taxes,
                    'origin': '{}:{}'.format(so['name'], so_line['id']),
                }
                self.merge_line(lines_by_hash, line)

        inv_lines = [[0, False, lines_by_hash[x]] for x in lines_by_hash]
        if len(inv_lines) < 1:
            LOGGER.error('Could not create invoice with no line. Hint: SOs already invoiced?')
            return False

        # Creating discount lines
        discount_lines = []
        for so in so_data:
            logging.info(f"Creating discounts for SO {so['name']}")
            discs = self.read('sale.discount.line', so['discount_lines'], ['id', 'discount_id', 'label', 'type', 'value', 'apply_to', 'product_ids', 'sequence_id'])
            for disc in discs:
                exdisc = next((d for d in discount_lines if d[2]['label'] == disc['label']), None)
                if not exdisc:
                    discount_lines.append([0, 0, {
                        'discount_id': disc['discount_id'][0],
                        'label': disc['label'],
                        'type': disc['type'],
                        'value': disc['value'],
                        'apply_to': disc['apply_to'],
                        'product_ids': [6, 0, disc['product_ids']] if disc['product_ids'] else False,
                        'sequence_id': disc['sequence_id'],
                    }])
                else:
                    if exdisc[2]['type'] == 'nominal' and disc['type'] == 'nominal':
                        exdisc[2]['value'] += disc['value']
        
        fp_accounts = self.search_read('account.fiscal.position.account', [['position_id', '=', inv_data['fiscal_position_id']]], ['account_src_id', 'account_dest_id'])
        fpos_account_map = {x['account_src_id'][0]: x['account_dest_id'][0] for x in fp_accounts}

        logging.info('Mapping accounts according to fiscal position')
        for il in inv_lines:
            acc_src = il[2]['account_id']
            acc_dest = fpos_account_map.get(acc_src, 0)
            if acc_dest:
                il[2]['account_id'] = acc_dest

        inv_data['invoice_line_ids'] = inv_lines
        inv_data['discount_lines'] = discount_lines
        tool.pfdebug(LOGGER, inv_data)

        invoice_id = self.create('account.invoice', inv_data)
        if not invoice_id:
            logging.error('Failed to create invoice')
            return False

        # Update sale order line (link SO line to Invoice line)
        invoice_lines = self.search_read('account.invoice.line', [['invoice_id', '=', invoice_id]], ['id', 'origin'])
        for line in invoice_lines:
            origins = line['origin'].split(',')
            sol_ids = []
            for org in origins:
                inf = org.split(':')
                if len(inf) > 1 and inf[1]:
                    sol_ids.append(int(inf[1]))
            if len(sol_ids) > 0:
                logging.debug('Linking SO Line {} <- Inv Line {}'.format(sol_ids, line['id']))
                self.write('sale.order.line', sol_ids, {'invoice_lines': [[6, 0, [line['id']]]]})

        return True

        
    def main(self):
        self.build_invoice_data()


if __name__ == '__main__':
    imtool = InvMerge()
    imtool.bootstrap()
    imtool.connect()
    imtool.main()
