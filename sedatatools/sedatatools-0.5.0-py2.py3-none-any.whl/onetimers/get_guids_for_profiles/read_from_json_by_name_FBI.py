from lxml import etree as et
import pandas as pd

config_variables = {
    'FBI2016': [
        'Total population',
        'Population density',
        'Age (# and %)',
        'Sex (# and %)',
        'Race (# and %)',
        'Hispanic or Latino by Race',
        'Educational Attainment for Population 25 years and over',
        'Estimated Households',
        'Households by Household Type',
        'Median Household Income',
        'Employment Status',
        'Employment/Unemployment Status by Race',
        'Work Experience',
        'Housing Units',
        'Housing Tenure',
        'Housing Occupancy Status',
        'Median monthly rent',
        'Median home value',
        'Mortgages consuming more than 30% of income',
        'Poverty rate',
        'Poverty by Age',
        'Poverty by Race',
        'Poverty by Household Type (e.g., poverty by single-parent household)',
    ],
    'FBI2016_labels': [
        'T002_001',
        'T002_002',
        'T002_003',
        'T004_001',
        'T004_002',
        'T004_003',
        'T004_004',
        'T004_005',
        'T004_006',
        'T006_001',
        'T006_002',
        'T006_003',
        'T006_004',
        'T008_001',
    ]
}


def get_new_guids_for_variables(acs_old_guid_elements, old_names):
    old_guids_by_names = {}
    old_names = [on.lower().replace('2015', '').replace('2016', '').replace('<dollaryear>', '') for on in old_names]
    try:
        vars = acs_old_guid_elements.xpath("//variable")
        for var in vars:
            if var.attrib['label'].lower().replace('2015', '').replace('2016', '').replace('<dollaryear>',
                                                                                           '') in old_names:
                new_name = var.attrib['name']
                new_label = var.attrib['label']
                new_guid = var.attrib['GUID']
                old_guids_by_names[new_guid.lower().replace('2015', '').replace('2016', '').replace('<dollaryear>',
                                                                                                    '') + new_label.lower().replace(
                    '2015', '').replace('2016', '').replace('<dollaryear>', '')] = [new_name, new_guid, new_label]
    except IndexError:
        print(f'Name not found in old xml file: {name}')
    return pd.DataFrame(old_guids_by_names).T


def get_new_guids_for_variables_by_name(acs_old_guid_elements, old_names):
    old_guids_by_names = {}
    old_names = [on.lower().replace('2015', '').replace('2016', '').replace('<dollaryear>', '') for on in old_names]
    tables = acs_old_guid_elements.xpath("//table")
    for table in tables:
        try:
            vars = table.xpath("./variable")
            for var in vars:
                if var.attrib['name'].lower().replace('2015', '').replace('2016', '').replace('<dollaryear>',
                                                                                               '') in old_names:
                    new_name = var.attrib['name']
                    new_label = var.attrib['label']
                    new_guid = var.attrib['GUID']
                    old_guids_by_names[new_guid.lower().replace('2015', '').replace('2016', '').replace('<dollaryear>',
                                                                                                        '') + new_label.lower().replace(
                        '2015', '').replace('2016', '').replace('<dollaryear>', '')] = [table.attrib['GUID'], table.attrib['name'], table.attrib['title'], new_guid, new_name, new_label]
        except IndexError:
            print(f'Name not found in old xml file: {name}')
    return pd.DataFrame(old_guids_by_names).T


def main():
    acs_1yr = et.parse('C:\Projects\Website-ASP.NET\pub\ReportData\Metadata\FBICrime_Popest_2015.xml')

    # guids_1yr_variables = get_new_guids_for_variables(acs_1yr, config_variables['FBI2016'])
    # guids_1yr_variables.to_csv('guids_FBI2016_variables_EDNW.csv', index=False)

    guids_1yr_variables = get_new_guids_for_variables_by_name(acs_1yr, config_variables['FBI2016_labels'])
    guids_1yr_variables.columns = ['table_guid', 'table_name', 'table_title', 'variable_guid', 'variable_name',
                                   'variable_label']
    guids_1yr_variables.to_csv('guids_FBI2016_variables_EDNW_labels.csv', index=False)


if __name__ == '__main__':
    main()
