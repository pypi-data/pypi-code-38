"""
Parameters for Locus Codes
"""

DIVS = set(['v', 'div', 'diva', 'divs', 'div4div', 'diva4diva', 'divi'])

GRANULARITY = [
    '1x6', '1x6x4'
    '4x1', '4x6', '4x6x4',
    '12x1', '12x6', '12x6x4',
    '36x1', '36x6', '36x6x4', 'full']

LOCUS_OUTPUT_TYPE = ['list', 'dict', 'string']

TABLE_OUTPUT_TYPE = ['path', 'df']

# barcode fields match those defined in the Barcodes model found at 
# https://github.com/LocusAnalytics/locus_db/blob/SPRINT/locus_db/database/models.py
BARCODE_FIELDS = ['enterprise_locus', 'intermediary_1_locus', 'intermediary_2_locus', 
                  'customer_locus', 'customer_department', 'customer_constituent_resource_1',
                  'customer_constituent_resource_1', 'customer_final_resource_1', 'customer_work_group_1',
                  'customer_constituent_resource_2', 'customer_final_resource_2', 'customer_work_group_2',
                  'cocustomer_locus', 'customer_of_customer_locus', 'customer_of_customer_department',
                  'customer_of_customer_constituent_resource_1', 'customer_of_customer_final_resource_1',
                  'customer_of_customer_work_group_1', 'customer_of_customer_constituent_resource_2',
                  'customer_of_customer_final_resource_2', 'customer_of_customer_work_group_2']

LOCUS_FIELDS = {'work': ['dr_category', 'dr_stage', 'dr_substage', 'act_4', 'act_12', 
                         'act_36', 'obj_category', 'obj_stage', 'obj_substage', 
                         'io_category', 'io_stage', 'io_substage'],
                'resource': ['subj_category', 'subj_stage', 'subj_substage', 'act_4', 
                             'act_12', 'act_36', 'obj_category', 'obj_stage', 
                             'obj_substage']}

ACT_GRAN_TO_FIELDS = {'1': [], '4': ['act_4'],
                      '12': ['act_4', 'act_12'], '36': ['act_4', 'act_12', 'act_36']}
RES_GRAN_TO_FIELDS = {'1': [], '6': ['category'], '6x4': [
    'category', 'stage'], '6x4x3': ['category', 'stage', 'substage']}

# {activity: requirement}
DR_LOCI = {'1': 'some', '2': 'some', '3': 'some', '1.1': 'some', '1.2': 'some',
           '1.3': 'some', '2.2': 'some', '3.1': 'some', '3.2': 'some',
           '1.1.2': 'some', '1.2.2': 'all', '1.2.3': 'all', '2.2.2': 'F',
           '1.3.2': 'some', '3.1.2': 'some', '3.2.2': 'all'}

IO_LOCI = {'1': 'some', '2': 'some', '3': 'some',  '4':'some',
           '1.1': 'all', '1.2': 'some', '1.3': 'some', '2.1': 'all',
           '2.2': 'some', '2.3': 'some', '3.1': 'some', '3.2': 'some',
           '3.3': 'some', '4.1': 'all', '4.2': 'some', '4.3': 'some',
           '1.1.1': 'all', '1.1.2': 'all', '1.1.3': 'all',
           '1.2.1': 'all', '1.3.1': 'some', '1.3.3': 'all',
           '2.1.1': 'all', '2.1.2': 'all', '2.1.3': 'all',
           '2.2.1': 'some', '2.3.1': 'all', '2.3.3': 'all',
           '3.1.1': 'all', '3.1.2': 'some', '3.1.3': 'all',
           '3.2.1': 'all', '3.2.3': 'all', '3.3.1': 'some',
           '3.3.3': 'all', '4.1.1': 'all', '4.1.2': 'all',
           '4.1.3': 'all', '4.2.1': 'all', '4.2.2': 'some',
           '4.2.3': 'some', '4.3.1': 'all', '4.3.2': 'all',
           '4.3.3': 'all'}
