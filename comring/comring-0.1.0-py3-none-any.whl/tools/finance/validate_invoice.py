from comring.lib import tool
import logging

LOGGER = logging.getLogger(__name__)

class VITool(tool.SimpleTool):

    def __init__(self):
        super().__init__()
        self.number = 'default'

    def boot_add_arguments(self, parser):
        super().boot_add_arguments(parser)
        parser.add_argument('number', type=int, help='Invoice number')

    def boot_process_arguments(self, args):
        super().boot_process_arguments(args)
        if args.number:
            self.number = args.number

    def main(self):
        inv_id = self.search('account.invoice', [['id', '=', self.number]], pos='one')
        if not inv_id:
            LOGGER.error('Invoice not found: %s', self.number)
            return False

        result = self.call('account.invoice', 'action_invoice_open', [inv_id], {})
        LOGER.info('Result : %r', result)

if __name__ == '__main__':
    vitool = VITool()
    vitool.bootstrap()
    vitool.connect()
    vitool.main()
