import os
import logging
from comring.lib import tool
from prettytable import PrettyTable
from . import mappers, loaders

MAPPING_FILE = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'data', 'mapping.xls')

LOGGER  = logging.getLogger(__name__)

class PayrollTool(tool.SimpleTool):
    payroll_file = ''
    journal_name = ''
    journal_id = 0
    date = ''
    group_data = None
    accounts_ok = False
    dc_ok = False

    def boot_add_arguments(self, parser):
        super().boot_add_arguments(parser)
        parser.add_argument('journal', help='Journal name')
        parser.add_argument('date', help='Date of journal entry (YYYY-MM-DD)')
        parser.add_argument('file', help='Payroll report file')

    def boot_process_arguments(self, args):
        super().boot_process_arguments(args)
        self.journal_name = args.journal
        self.date = args.date
        self.payroll_file = args.file

    def identify_journal(self):
        self.journal_id = self.search('account.journal', [['name', '=', self.journal_name]], pos='one')

    def identify_accounts(self):
        names = list(set([self.group_data[gkey]['acc_group'] for gkey in self.group_data]))
        accounts = self.search_read('account.account', [['name', 'in', names]], ['id', 'code', 'name'])
        accounts_map = {acc['name']: acc for acc in accounts}

        self.accounts_ok = True
        for gkey in self.group_data:
            g = self.group_data[gkey]
            g['account_id'] = 0
            g['account_code'] = ''
            g['account_name'] = ''
            acc = accounts_map.get(g['acc_group'], None)
            if not acc:
                LOGGER.warn('Account not found in Odoo: %s', g['acc_group'])
                self.accounts_ok = False
                continue
            g['account_id'] = acc['id']
            g['account_code'] = acc['code']
            g['account_name'] = acc['name']
        return True

    def get_dc(self):
        names = list(set([self.group_data[gkey]['dc'] for gkey in self.group_data]))
        dcs = self.search_read('res.partner', [['name', 'in', names], ['is_dc', '=', True]], ['id', 'name'])
        dc_map = {dc['name']: dc for dc in dcs}

        self.dc_ok = True
        for gkey in self.group_data:
            g = self.group_data[gkey]
            g['dc_id'] = 0
            dc = dc_map.get(g['dc'], None)
            if not dc:
                LOGGER.warn('DC not found in odoo: %s', g['dc'])
                self.dc_ok = False
                continue
            g['dc_id'] = dc['id']
        return True

    def report_stdout(self):
        pt = PrettyTable()
        pt.field_names = ["Account", "DC", "Debit", "Credit", "Account Code"]
        pt.sortby = 'Debit'
        pt.reversesort = True
        pt.align['Account'] = 'l'
        pt.align['DC'] = 'l'
        pt.align['Debit'] = 'r'
        pt.align['Credit'] = 'r'
        for gkey in self.group_data:
            g = self.group_data[gkey]
            pt.add_row([
                g['acc_group'],
                g['dc'],
                str(g['value']) if g['type'] == 'debit' else '',
                str(g['value']) if g['type'] == 'credit' else '',
                g['account_code'],
            ])
        print(pt)

    def create_je(self):
        je_data = {
            'date': self.date,
            'ref': 'Percobaan Payroll',
            'journal_id': self.journal_id,
        }

        j_items = []
        for gkey in self.group_data:
            gd = self.group_data[gkey]
            j_items.append((0, 0, {
                'account_id': gd['account_id'],
                'name': gd['acc_group'],
                'dc_id': gd['dc_id'],
                'debit': gd['value'] if gd['type'] == 'debit' else 0,
                'credit': gd['value'] if gd['type'] == 'credit' else 0
            }))

        je_data['line_ids'] = j_items

        res = self.create('account.move', je_data)
        LOGGER.info('Journal Entry created: %r', res)
    
    def main(self):
        # Load mapper
        mapper = mappers.Mapper()
        mapper.load(MAPPING_FILE)

        # Load data
        loader = loaders.XLSLoader()
        loader.load(self.payroll_file)

        # Map data
        self.group_data = mapper.map_by_keyword_matching(loader.detail_dept)
        
        # Identify journal
        self.identify_journal()

        # Identify accounts
        self.identify_accounts()

        # Identify DC
        self.get_dc()

        # Report as table
        self.report_stdout()

        # Create JE
        self.create_je()

if __name__ == '__main__':
    tool = PayrollTool()
    tool.bootstrap()
    tool.connect()
    tool.main()
