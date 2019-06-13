from comring.lib import tool, cache
import logging
import csv

LOGGER = logging.getLogger(__name__)

class DiscountCache():
    def __init__(self):
        self.all = []
        self.by_id = {}

    def load(self, client):
        LOGGER.info('Loading discounts data to cache')
        self.all = client.search_read('discount.discount', [['id', '!=', False]], ['id', 'name', 'brand', 'sequence_discount', 'percentage', 'account_id'])
        self.by_id = {d['id']: d for d in self.all}
        return True

class InvTotalBrand():
    def __init__(self, instance):
        self.inv_domain = []
        self.product_cache = None
        self.discount_cache = None
        self.categ_cache = None
        self.instance = instance

        self.product_cache_fields = ('id', 'name', 'lst_price', 'standard_price', 'categ_id', 'product_brand_id')
        self.category_cache_fields = ('id', 'name', 'property_account_income_categ_id')
        self.coa_cache_fields = ('id', 'code', 'name')
        self.partner_cache_fields = ('id', 'ref', 'name')

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

    def calculate_discount_line(self, line_gross, brand_data, invl):
        disc_list = [self.discount_cache.by_id[d_id] for d_id in invl.get('discount_m2m', [])]
        sorted_discounts = sorted(disc_list, key=lambda x: x['sequence_discount'])
        gross_amt = line_gross
        for disc in sorted_discounts:
            disc_brand = disc['brand'][1]
            disc_account = self.account_cache.read(disc['account_id'][0])
            disc_column = self.account_mapping.get(disc_account['code'])
            if not disc_column:
                LOGGER.warn('No mapping for discount account: %s - %s', disc_account['code'], disc_account['name'])
                continue
            
            disc_val = gross_amt * disc['percentage'] * 0.01
            gross_amt -= disc_val

            brand_data[disc_column] += disc_val
    
    def calculate_discount_global(self, by_brand_by_account, inv):
        pass

    def main(self):
        # Check search domain, don't continue if it's empty
        if not self.inv_domain:
            LOGGER.error('Invalid invoice search criteria: %r', self.inv_domain)
            return False

        # Load invoice data
        LOGGER.debug('Invoice search criteria: %r', self.inv_domain)
        invoices = self.instance.client.search_read('account.invoice', self.inv_domain, ['id', 'number', 'name', 'origin', 'partner_id', 'create_date', 'date_invoice'])
        LOGGER.info('Invoice matching criteria: %d', len(invoices))

        # Sanity check
        if not invoices:
            return False

        # Load discount cache
        LOGGER.info('Loading discount cache')
        self.discount_cache = DiscountCache()
        self.discount_cache.load(self.instance.client)

        # Load product cache
        LOGGER.debug('Loading product cache')
        self.product_cache = cache.SimpleCache(self.instance.client, 'product.product', self.product_cache_fields)

        # Load category cache
        LOGGER.debug('Loading product category cache')
        self.categ_cache = cache.SimpleCache(self.instance.client, 'product.category', self.category_cache_fields)

        # Load chart of account cache
        LOGGER.debug('Loading chart of account cache')
        self.account_cache = cache.SimpleCache(self.instance.client, 'account.account', self.coa_cache_fields)

        # Load partner cache
        LOGGER.debug('Loading partner cache')
        self.partner_cache = cache.SimpleCache(self.instance.client, 'res.partner', self.partner_cache_fields)

        inv_by_brand = {}

        # Process each invoice
        for inv in invoices:
            LOGGER.info('Processing %s', inv['number'])

            partner = self.partner_cache.read(inv['partner_id'][0])
            by_brand_by_account = {}
            
            # Read invoice lines for this invoice
            inv_lines = self.instance.client.search_read('account.invoice.line', [['invoice_id', '=', inv['id']]], ['id', 'product_id', 'product_brand', 'account_id', 'name', 'quantity', 'price_unit', 'discount_m2m'])

            # Prefetch product data
            product_ids = [il['product_id'][0] for il in inv_lines]
            if product_ids:
                self.product_cache.prefetch(product_ids)

            # Process each line
            for invl in inv_lines:
                # Get product
                line_product = self.product_cache.read(invl['product_id'][0])

                # Get category
                line_product_categ = self.categ_cache.read(line_product['categ_id'][0])

                # Skip lines without product brand (and possible, without product)
                brand = None
                if invl.get('product_brand', False):
                    brand = invl['product_brand'][1]
                else:
                    if line_product.get('product_brand_id', False):
                        brand = line_product['product_brand_id'][1]
                
                if not brand:
                    LOGGER.warn('  No brand info on line %s', invl['name'])
                    continue

                # 3 important values: brand, account, and gross
                line_account = self.account_cache.read(invl['account_id'][0])
                line_gross = invl['quantity'] * invl['price_unit']

                # Get account to column mapping
                line_column = self.account_mapping.get(line_account['code'], None)
                if not line_column:
                    LOGGER.warn('No mapping for account: %s - %s', line_account['code'], line_account['name'])
                    continue

                # cogs is calculated from product's list price
                line_cogs = invl['quantity'] * self.get_cost_price(line_product)

                # Data by brand, by account
                brand_data = by_brand_by_account.setdefault(brand, {
                    'Invoice Date': inv['date_invoice'],
                    'Partner Name': partner['name'],
                    'Partner ID': partner['ref'],
                    'Number': inv['number'],
                    'Brand': brand,
                    'Gross Sales': 0, 'Promo Discount': 0, 'Margin Discount': 0,
                    'Cash Discount': 0, 'Distribution Fee Discount': 0, 'Sales Discount Forfeited': 0,
                    'Tax': 0,
                    'Total Amount': 0,
                    'GT Price': 0
                })
                brand_data[line_column] += abs(line_gross)
                if line_column == 'Gross Sales':
                    brand_data['GT Price'] += abs(line_cogs)

                # Now calculate discounts on line
                self.calculate_discount_line(line_gross, brand_data, invl)
            
            self.calculate_discount_global(by_brand_by_account, inv)

            # Calculate Tax & AR
            for brand in by_brand_by_account:
                brand_data = by_brand_by_account[brand]
                untaxed = brand_data['Gross Sales'] - brand_data['Promo Discount'] - brand_data['Margin Discount'] - brand_data['Cash Discount'] - brand_data['Distribution Fee Discount'] - brand_data['Sales Discount Forfeited']
                brand_data.update({
                    'Tax': untaxed * 0.1,
                    'Total Amount': untaxed * 1.1
                })
            inv_by_brand[inv['number']] = by_brand_by_account
            
        return inv_by_brand

class InvTotalBrandNBM(InvTotalBrand):

    def get_cost_price(self, product):
        return product['standard_price']
    
    def calculate_discount_global(self, by_brand_by_account, inv):
        temp_gross = {}
        discount_lines = self.instance.client.search_read('account.discount.line', [['invoice_id', '=', inv['id']]], ['id', 'sequence_id', 'discount_id', 'account_id', 'type', 'value'])
        sorted_disc_line = sorted(discount_lines, key=lambda x: x['sequence_id'])
        for disc_line in sorted_disc_line:
            disc = self.discount_cache.by_id[disc_line['discount_id'][0]]
            brand = disc['brand'][1]
            brand_data = by_brand_by_account.get(brand, None)
            acc = self.account_cache.read(disc['account_id'][0])
            disc_column = self.account_mapping.get(acc['code'], None)
            if not disc_column:
                LOGGER.warning('No mapping for account: [{}] {}'.format(acc['code'], acc['name']))
                continue

            if not brand_data:
                # No transaction for this brand, skip
                continue
            temp_gross.setdefault(brand, brand_data['Gross Sales'])
            disc_val = 0
            if disc_line['type'] == 'percentage':
                disc_val = temp_gross[brand] * disc_line['value'] * 0.01
            if disc_line['type'] == 'nominal':
                disc_val = disc_line['value']

            if disc_val:
                temp_gross[brand] -= disc_val
                brand_data[disc_column] += disc_val


class InvTotalBrandTool(tool.SimpleTool):

    def __init__(self):
        super().__init__()
        self.inv_domain = []

    def boot_add_arguments(self, parser):
        super().boot_add_arguments(parser)
        parser.add_argument('-n', '--numbers', help='Invoice numbers')
        parser.add_argument('-d', '--date', help='Invoice date')
        parser.add_argument('-c', '--creation-date', help='Invoice creation date')
        return True

    def boot_process_arguments(self, args):
        super().boot_process_arguments(args)

        self.inv_domain = []
        if args.numbers:
            self.inv_domain += [['number', 'in', args.numbers.split(',')]]
        if args.date:
            self.inv_domain += [['date_invoice', '=', args.date]]
        if args.creation_date:
            self.inv_domain += [['create_date', '=', args.creation_date]]

        if not self.inv_domain:
            LOGGER.error('You must supply at least one of: number, date, or creation-date')
            return False

        self.inv_domain += [['state', 'not in', ['draft', 'proforma', 'proforma2']]]
        return True

    def main(self):
        itb = None
        if self._instance.kind == 'live':
            itb = InvTotalBrand(self._instance)
        elif self._instance.kind == 'nbm':
            itb = InvTotalBrandNBM(self._instance)
        else:
            LOGGER.error('Unsupported env kind %s', self._instance.kind)
            return False

        itb.inv_domain = self.inv_domain
        
        inv_by_brand = itb.main()
        
        # Open output file for writing
        output_file_name = '/tmp/inv_by_brand.csv'
        csv_file = open(output_file_name, 'wt')
        csv_writer = csv.writer(csv_file)
       
        csv_columns = ['Invoice Date', 'Partner Name', 'Partner ID', 'Number', 'Brand',
                'Gross', 'Promo Discount', 'Margin Discount', 'Cash Discount', 'Distribution Fee Discount', 'GT Price']
        csv_writer.writerow(csv_columns)
        
        if inv_by_brand:
            for inv in inv_by_brand:
                by_brand_by_account = inv_by_brand[inv]
                # Write result for this invoice to file
                for brand in by_brand_by_account:
                    brand_data = by_brand_by_account[brand]
                    csv_writer.writerow([
                        brand_data['Invoice Date'],
                        brand_data['Partner Name'],
                        brand_data['Partner ID'],
                        brand_data['Number'],
                        brand_data['Brand'],
                        brand_data['Gross Sales'],
                        brand_data['Promo Discount'],
                        brand_data['Margin Discount'],
                        brand_data['Cash Discount'],
                        brand_data['Distribution Fee Discount'],
                        brand_data['GT Price']
                    ])

        csv_file.flush()
        csv_file.close()


if __name__ == '__main__':
    itbtool = InvTotalBrandTool()
    if itbtool.bootstrap():
        itbtool.connect()
        itbtool.main()
