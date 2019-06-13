from xlrd import open_workbook
import logging
import re

LOGGER  = logging.getLogger(__name__)

def sheet_to_dict_list(sheet):
    """
    This method is used to convert an excel sheet into a list of dictionary
    with column label as their key.
    """
    keys = [sheet.cell(0, col_index).value for col_index in range(sheet.ncols)]
    dict_list = []
    for row_index in range(1, sheet.nrows):
        dict_list.append(
            { keys[col_index]: sheet.cell(row_index, col_index).value for col_index in range(sheet.ncols) }
        )

    return dict_list

class Mapper(object):
    def __init__(self):
        self.comp_map = {}
        self.dept_map_list = []
        self.keywords = []

    def load(self, file_name):
        """
        This function loads mapping sheets
        """
        wb = open_workbook(file_name)

        comp_sheet = wb.sheet_by_name('comp_map')
        lst = sheet_to_dict_list(comp_sheet)
        self.comp_map = { d['component']: d for d in lst }

        dept_sheet = wb.sheet_by_name('dept_map')
        self.dept_map_list = sheet_to_dict_list(dept_sheet)

        keywords_sheet = wb.sheet_by_name('keywords')
        self.keyword_list = sheet_to_dict_list(keywords_sheet)
        
        return True

    def get_account_for_dept(self, dept, component):
        """
        Get account for departement and component based on department pattern matching
        """
        # First, get suffix or mapping according to dept_map_list data
        suffix = ''
        remap_to = ''
        acc_group = self.comp_map.get(component, None)
        if not acc_group:
            LOGGER.warn('Component not found in mapping: %s', component)
            return (None, None)

        acc_group_account = acc_group['account_group']
        acc_group_type = acc_group['type']
        for dept_map in self.dept_map_list:
            if re.match(dept_map['pattern'], dept):
                suffix = dept_map['suffix']
                if acc_group_account == dept_map['remap_from']:
                    remap_to = dept_map['remap_to']
        if remap_to:
            acc_group_account = remap_to
        return (f'{acc_group_account}{suffix}', acc_group_type)

    def get_account_for_dept_keyword(self, dept, component):
        """
        Get account for department and component based on keyword checking
        """
        account_data = {
            'acc_group': None,
            'dc': None
        }
        suffix = ''
        remap_to = ''
        acc_group = self.comp_map.get(component, None)
        if not acc_group:
            LOGGER.warn('Component not found in mapping: %s', component)
            return {}

        account_data['acc_group'] = acc_group['account_group']
        account_data['type'] = acc_group['type']
        account_data['dc'] = 'HEAD OFFICE'

        for kwd in self.keyword_list:
            dept_pat = f"(^|.+\s+){kwd['dept_keyword']}(\s+.+|$)"
            dept_match = re.match(dept_pat, dept)
            component_match = re.match(kwd['component_pattern'], component)
            if dept_match and component_match:
                action = kwd['action']
                if action == 'setdc':
                    account_data['dc'] = kwd['value1']
                if action == 'suffix':
                    suffix = kwd['value1']
                if action == 'map':
                    account_data['acc_group'] = kwd['value1']

        if suffix and account_data['acc_group']:
            account_data['acc_group'] = '{}{}'.format(account_data['acc_group'], suffix)

        return account_data

    def map_by_keyword_matching(self, dept_data_map):
        """
        Group data per account group with keyword mathching on department and component
        """
        # This is the variable to hold the result. It will be a dictionary
        # with account_group, type, and dc as their key
        groups = {}
        
        # Iterate departments
        for dept in dept_data_map:
            dept_data = dept_data_map[dept]
            for comp in dept_data:
                # Map account
                acc_data = self.get_account_for_dept_keyword(dept, comp)
                if not acc_data:
                    continue
                key = '{}:{}:{}'.format(
                        acc_data['acc_group'],
                        acc_data['type'],
                        acc_data['dc']
                        )
                acc_data['value'] = 0
                group_data = groups.setdefault(key, acc_data)
                group_data['value'] += dept_data[comp]
        return groups

    def group_by_account(self, dept_data_map):
        """
        Group data per account group according to comp_map data
        """
        # This is the variable to hold the result. It will be a dictionary
        # with account_group as their key
        groups = {}

        # Iterate sections
        for dept in dept_data_map:
            dept_data = dept_data_map[dept]
            for comp in dept_data:
                # Get account suffix/remap
                acc_group_account, acc_group_type = self.get_account_for_dept(dept, comp)
                if not acc_group_account:
                    continue
                group_key = f'{acc_group_account}:{acc_group_type}'
                group_data = groups.setdefault(group_key, {'acc_group': acc_group_account, 'type': acc_group_type, 'value': 0})
                group_data['value'] += dept_data[comp]

        return groups


