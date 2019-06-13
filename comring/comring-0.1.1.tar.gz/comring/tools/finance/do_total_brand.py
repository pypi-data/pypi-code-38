from comring.lib import tool, cache
import logging
import csv
import re

LOGGER = logging.getLogger(__name__)

class DOTotalBrand():
    def __init__(self, instance):
        self.do_domain = []
        self.product_cache = None
        self.categ_cache = None
        self.instance = instance

        self.account_mapping = {
            # Sales accounts
            '4101001001': 'Gross Sales',
            '4101001002': 'Gross Sales',
            '4101002001': 'Gross Sales',
            '4101002002': 'Gross Sales',
            '4101003001': 'Gross Sales',
            '4101003002': 'Gross Sales',
            '4101004001': 'Gross Sales',
            '4101004002': 'Gross Sales',
            '410101001': 'Gross Sales',
            '410101002': 'Gross Sales',
            '410102001': 'Gross Sales',
            '410102002': 'Gross Sales',
            '410103001': 'Gross Sales',
            '410103002': 'Gross Sales',
            '410104001': 'Gross Sales',
            '410104002': 'Gross Sales',
            
            # Discount accounts
            '4102001001': 'Margin Discount',
            '4102001002': 'Cash Discount',
            '4102001003': 'Promo Discount',
            '4102001004': 'Distribution Fee Discount',
            '4102001005': 'Sales Discount Forfeited',
            '410201001': 'Margin Discount',
            '410201002': 'Cash Discount',
            '410201003': 'Promo Discount',
            '410201004': 'Distribution Fee Discount',
            '410201005': 'Sales Discount Forfeited'
        }

    def get_cost_price(self, product):
        return product['lst_price']

    def main(self):
        # Check search domain, don't continue if it's empty
        if not self.do_domain:
            LOGGER.error('Invalid DO search criteria: %r', self.do_domain)
            return False

        # Load invoice data
        LOGGER.debug('DO search criteria: %r', self.do_domain)
        pickings = self.instance.client.search_read('stock.picking', self.do_domain, ['id', 'name', 'origin', 'partner_id', 'create_date', 'date_done'])
        LOGGER.info('DO matching criteria: %d', len(pickings))

        # Sanity check
        if not pickings:
            return False

        # Load product cache
        LOGGER.info('Loading product cache')
        self.product_cache = cache.SimpleCache(self.instance.client, 'product.product', ['id', 'name', 'price', 'lst_price', 'standard_price', 'categ_id', 'tags', 'product_brand_id'])

        # Load product tags (for brand)
        LOGGER.info('Loading product brands cache')
        self.tags_cache = cache.SimpleCache(self.instance.client, 'product.brand', ['id', 'name'])

        # Load category cache
        LOGGER.info('Loading product category cache')
        self.categ_cache = cache.SimpleCache(self.instance.client, 'product.category', ['id', 'name', 'property_account_income_categ_id'])

        # Load chart of account cache
        LOGGER.info('Loading chart of account cache')
        self.account_cache = cache.SimpleCache(self.instance.client, 'account.account', ['id', 'code', 'name'])
        
        # Load partner cache
        LOGGER.info('Loading partner cache')
        self.partner_cache = cache.SimpleCache(self.instance.client, 'res.partner', ['id', 'ref', 'name'])

        picking_by_brand = {}

        # Process each invoice
        for pick in pickings:
            LOGGER.info('Processing %s', pick['name'])
            
            partner = None
            if pick['partner_id']:
                partner = self.partner_cache.read(pick['partner_id'][0])
            
            picking_brands = {}
            
            # Read invoice lines for this invoice
            stock_moves = self.instance.client.search_read('stock.move', [['picking_id', '=', pick['id']]], ['id', 'product_id', 'name', 'product_uom_qty'])

            # Prefetch product data
            product_ids = [sm['product_id'][0] for sm in stock_moves]
            if product_ids:
                self.product_cache.prefetch(product_ids)

            # Process each line
            for smv in stock_moves:
                # Get product
                line_product = self.product_cache.read(smv['product_id'][0])

                # Get category
                line_product_categ = self.categ_cache.read(line_product['categ_id'][0])

                # Determine brand
                brand = None
                # First check product tags (Odoo live style)
                if line_product.get('tags', False):
                    for tid in line_product['tags']:
                        tag = self.tags_cache.read(tid)
                        if tag:
                            mbrand = re.match(r'brand:(.+)', tag['name'])
                            if mbrand:
                                brand = mbrand.group(1)
                # Second, check product_brand_id field (Odoo NBM style)
                if not brand and line_product.get('product_brand_id', False):
                    brand = line_product['product_brand_id'][1]
                # Give up
                if not brand:
                    LOGGER.warn('No brand info on line %s', smv['name'])
                    continue

                line_cost = smv['product_uom_qty'] * self.get_cost_price(line_product)

                pbdata = picking_brands.setdefault(brand, {
                    'Date': pick['date_done'],
                    'Partner Name': partner['name'] if partner else '',
                    'Partner ID': partner['ref'] if partner else '',
                    'Number': pick['name'],
                    'Brand': brand,
                    'Cost': 0
                })

                pbdata['Cost'] += line_cost

            picking_by_brand[pick['name']] = picking_brands
            
        return picking_by_brand

class DOTotalBrandNBM(DOTotalBrand):

    def get_cost_price(self, product):
        return product['standard_price']
    

class DOTotalBrandTool(tool.SimpleTool):

    def __init__(self):
        super().__init__()
        self.do_domain = []

    def boot_add_arguments(self, parser):
        super().boot_add_arguments(parser)
        parser.add_argument('-n', '--numbers', help='DO numbers')
        parser.add_argument('-d', '--date', help='DO validation date')
        parser.add_argument('-c', '--creation-date', help='DO creation date')
        return True

    def boot_process_arguments(self, args):
        super().boot_process_arguments(args)

        self.do_domain = []
        if args.numbers:
            self.do_domain += [['name', 'in', args.numbers.split(',')]]
        if args.date:
            self.do_domain += [['date_done', '=', args.date]]
        if args.creation_date:
            self.do_domain += [['create_date', '=', args.creation_date]]

        if not self.do_domain:
            LOGGER.error('You must supply at least one of: number, date, or creation-date')
            return False

        self.do_domain += [['state', 'in', ['done']]]
        return True

    def main(self):
        dotb = None
        if self._instance.kind == 'live':
            dotb = DOTotalBrand(self._instance)
        elif self._instance.kind == 'nbm':
            dotb = DOTotalBrand(self._instance)
        else:
            LOGGER.error('Unsupported instance kind %s', self._instance.kind)
            return False
        
        dotb.do_domain = self.do_domain
        
        do_by_brand = dotb.main()
        
        # Open output file for writing
        output_file_name = '/tmp/do_by_brand.csv'
        csv_file = open(output_file_name, 'wt')
        csv_writer = csv.writer(csv_file)
       
        csv_columns = ['Date', 'Partner Name', 'Partner ID', 'Number', 'Brand', 'Cost']
        csv_writer.writerow(csv_columns)
        
        for picking in do_by_brand:
            by_brand = do_by_brand[picking]
            # Write result for this invoice to file
            for brand in by_brand:
                brand_data = by_brand[brand]
                row_data = [brand_data[col] for col in csv_columns]
                csv_writer.writerow(row_data)

        csv_file.flush()
        csv_file.close()


if __name__ == '__main__':
    dotbtool = DOTotalBrandTool()
    if dotbtool.bootstrap():
        dotbtool.connect()
        dotbtool.main()
