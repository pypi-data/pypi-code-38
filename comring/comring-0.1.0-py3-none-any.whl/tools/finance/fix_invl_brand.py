from comring.lib import tool, cache
import logging

LOGGER = logging.getLogger(__name__)

class MyTool(tool.SimpleTool):

    def __init__(self):
        super().__init__()

    def boot_add_arguments(self, parser):
        return super().boot_add_arguments(parser)

    def boot_process_arguments(self, args):
        return super().boot_process_arguments(args)

    def main(self):
        product_cache = cache.SimpleCache(self.get_client(), 'product.product', ['id', 'brand'], 'id')
        brand_cache = cache.SimpleCache(self.get_client(), 'product.brand', ['id', 'name'], 'id')

        inv_lines = self.search_read('account.invoice.line', [['product_brand', '=', False], ['product_id', '!=', False]], ['id', 'product_id'])

        prod_ids = list(set([l['product_id'][0] for l in inv_lines]))
        product_cache.prefetch(prod_ids)

        LOGGER.info('Lines to fix: %d', len(inv_lines))

if __name__ == '__main__':
    mytool = MyTool()
    mytool.bootstrap()
    mytool.connect()
    mytool.main()
