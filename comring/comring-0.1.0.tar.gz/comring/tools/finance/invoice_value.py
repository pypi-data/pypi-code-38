from comring.lib import tool
import logging
import csv

LOGGER = logging.getLogger(__name__)

class InvValueTool(tool.SimpleTool):

    def __init__(self):
        super().__init__()
        self.dc = ''
        self.date_criteria = ''
        self.output_file = ''

    def boot_add_arguments(self, parser):
        super().boot_add_arguments(parser)
        parser.add_argument('dc', help='DC Name (exact match)')
        parser.add_argument('date', help='Date criteria (format: yyyy-mm-dd')
        parser.add_argument('output_file', help='Output file')

    def boot_process_arguments(self, args):
        super().boot_process_arguments(args)
        self.dc = args.dc
        self.date_criteria = args.date
        self.output_file = args.output_file

    def main(self):
        dc_id = self.search('res.partner', [['is_dc', '=', True], ['name', '=', self.dc]], pos='one')
        if not dc_id:
            LOGGER.error('DC not found: %s', self.dc)
            return False

        domain = [['date_invoice', '=', self.date_criteria],['state', '=', 'open'], ['dc_id', '=', self.dc]]
        invoices = self.search_read('account.invoice', domain, ['id', 'number', 'date_invoice', 'partner_id', 'dc_id', 'amount_untaxed', 'amount_total'])

        brands = []
        invoice_by_brand = {}

        LOGGER.info('Building data')
        for inv in invoices:
            LOGGER.debug('Processing invoice %s', inv['number'])
            res = self.call('account.invoice', 'get_invoice_data', [inv['id']], {})
            
            amount_total = res['amount_total']
            by_brand = invoice_by_brand.setdefault(inv['number'], {
                'number': inv['number'],
                'customer': inv['partner_id'][1],
                'date_invoice': inv['date_invoice'],
                'by_brand': {},
            })['by_brand']
            for lg in res['line_groups']:
                brand = lg['name']
                if brand not in brands:
                    brands.append(brand)
                by_brand[brand] = {
                    'discounts': lg['discounts'],
                    'name': lg['name'],
                    'subtotal': lg['subtotal'],
                    'net_price': lg['net_price'],
                }

        LOGGER.info('Writing result')
        with open(self.output_file, 'w') as f:
            outwriter = csv.writer(f, delimiter='\t')
            disc_count = 6
            header_row1 = ['Number', 'Date', 'Customer', 'Brand', 'Gross']
            for x in range(0, disc_count):
                header_row1 += ['Disc #{}'.format(x+1), '']
            header_row1 += ['Net']

            outwriter.writerow(header_row1)

            for inv_number in invoice_by_brand:
                inv = invoice_by_brand[inv_number]
                row = [
                    inv['number'],
                    inv['date_invoice'],
                    inv['customer'],
                ]
                for inv_brand in inv['by_brand']:
                    inv_brand_data = inv['by_brand'][inv_brand]
                    row += [
                        inv_brand,
                        inv_brand_data['subtotal'],
                    ]
                    for disx in range(0, disc_count):
                        if disx < len(inv_brand_data['discounts']):
                            disc_data = inv_brand_data['discounts'][disx]
                            row += [
                                disc_data['name'],
                                disc_data['amount']
                            ]
                        else:
                            row += ['', '']
                    row += [inv_brand_data['net_price']]
                outwriter.writerow(row)

if __name__ == '__main__':
    invtool = InvValueTool()
    invtool.bootstrap()
    invtool.connect()
    invtool.main()
