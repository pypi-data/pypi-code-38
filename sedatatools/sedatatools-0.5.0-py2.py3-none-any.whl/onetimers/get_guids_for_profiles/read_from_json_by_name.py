from lxml import etree as et
import pandas as pd

config_variables = {
    'ACS2016': [
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
    'ACS2016_labels': [
        'T001_001',
        'T002_001',
        'T007_001',
        'T007_002',
        'T007_003',
        'T007_004',
        'T007_005',
        'T007_006',
        'T007_007',
        'T007_008',
        'T007_009',
        'T007_010',
        'T007_011',
        'T007_012',
        'T007_013',
        'T004_001',
        'T004_002',
        'T004_003',
        'T013_001',
        'T013_002',
        'T013_003',
        'T013_004',
        'T013_005',
        'T013_006',
        'T013_007',
        'T013_008',
        'T014_001',
        'T014_002',
        'T014_003',
        'T014_004',
        'T014_005',
        'T014_006',
        'T014_007',
        'T014_008',
        'T014_009',
        'T014_010',
        'T014_011',
        'T014_012',
        'T014_013',
        'T014_014',
        'T014_015',
        'T014_016',
        'T014_017',
        'T025_001',
        'T025_002',
        'T025_003',
        'T025_004',
        'T025_005',
        'T025_006',
        'T025_007',
        'T025_008',
        'T017_001',
        'T017_002',
        'T017_003',
        'T017_004',
        'T017_005',
        'T017_006',
        'T017_007',
        'T017_008',
        'T017_009',
        'T057_001',
        'T033_001',
        'T033_002',
        'T033_003',
        'T033_004',
        'T033_005',
        'T033_006',
        'T033_007',
        'T046_001',
        'T046_002',
        'T046_003',
        'T065_001',
        'T065_002',
        'T065_003',
        'T065_004',
        'T065_005',
        'T065_006',
        'T065_007',
        'T093_001',
        'T094_003',
        'T094_001',
        'T094_002',
        'T095_001',
        'T095_002',
        'T095_003',
        'T236_001',
        'T236_002',
        'T236_003',
        'T236_004',
        'T236_005',
        'T236_006',
        'T236_007',
        'T236_008',
        'T236_009',
        'T236_010',
        'T236_011',
        'T101_001',
        'T114_001',
        'T114_002',
        'T114_003',
        'T115_001',
        'T115_002',
        'T115_003',
        'T116_001',
        'T116_002',
        'T116_003',
        'T119_001',
        'T119_002',
        'T119_003',
        'T120_001',
        'T120_002',
        'T120_003',
        'T121_001',
        'T121_002',
        'T121_003',
        'T122_001',
        'T122_002',
        'T122_003',
        'T123_001',
        'T123_002',
        'T123_003',
        'T124_001',
        'T124_002',
        'T124_003',
        'T126_001',
        'T126_002',
        'T126_003',
    ]
}


def get_new_guids_for_variables(acs_old_guid_elements, old_names):
    old_guids_by_names = {}
    old_names = [on.lower().replace('2015', '').replace('2016', '').replace('<dollaryear>', '') for on in old_names]
    try:
        variables = acs_old_guid_elements.xpath("//variable")
        for var in variables:
            if var.attrib['label'].lower().replace('2015', '').replace('2016', '').replace('<dollaryear>',
                                                                                           '') in old_names:
                new_name = var.attrib['name']
                new_label = var.attrib['label']
                new_guid = var.attrib['GUID']
                old_guids_by_names[new_guid.lower().replace('2015', '').replace('2016', '').replace('<dollaryear>', '')
                                   + new_label.lower().replace(
                    '2015', '').replace('2016', '').replace('<dollaryear>', '')] = [new_name, new_guid, new_label]
    except IndexError:
        print(f'Name not found in old xml file: {var}')
    return pd.DataFrame(old_guids_by_names).T


def get_new_guids_for_variables_by_name(acs_old_guid_elements, old_names):
    old_guids_by_names = {}
    old_names = [on.lower().replace('2015', '').replace('2016', '').replace('<dollaryear>', '') for on in old_names]
    tables = acs_old_guid_elements.xpath("//table")
    for table in tables:
        try:
            variables = table.xpath("./variable")
            for var in variables:
                if var.attrib['name'].lower().replace('2015', '').replace('2016', '').replace('<dollaryear>',
                                                                                              '') in old_names:
                    new_name = var.attrib['name']
                    new_label = var.attrib['label']
                    new_guid = var.attrib['GUID']
                    old_guids_by_names[new_guid.lower().replace('2015', '').replace('2016', '')
                                           .replace('<dollaryear>', '') + new_label.lower().replace(
                        '2015', '').replace('2016', '').replace('<dollaryear>', '')] = [table.attrib['GUID'],
                                                                                        table.attrib['name'],
                                                                                        table.attrib['title'],
                                                                                        new_guid,
                                                                                        new_name, new_label]
        except IndexError:
            print(f'Name not found in old xml file: {table}')
    return pd.DataFrame(old_guids_by_names).T


def main():
    # read xml file
    acs_1yr = et.parse('C:\Projects\Website-ASP.NET\pub\ReportData\Metadata\ACS 2016-1yr metadata.xml')

    guids_1yr_variables = get_new_guids_for_variables(acs_1yr, config_variables['ACS2016'])
    guids_1yr_variables.to_csv('guids_ACS_2016_1yr_variables_EDNW.csv', index=False)

    guids_1yr_variables = get_new_guids_for_variables_by_name(acs_1yr, config_variables['ACS2016_labels'])
    guids_1yr_variables.columns = ['table_guid', 'table_name', 'table_title', 'variable_guid', 'variable_name',
                                   'variable_label']
    guids_1yr_variables.to_csv('guids_ACS_2016_1yr_variables_EDNW_labels.csv', index=False)


if __name__ == '__main__':
    main()
