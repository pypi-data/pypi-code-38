def run_test_11(inputXML):
    # list of tables not visible in report and/or map

    print('INFO: Test 11 started..')
    notFound=True
    for table in inputXML.findall('SurveyDatasets/SurveyDataset/tables/table'):
        if table.get('Visible') == 'false' and table.get('VisibleInMaps') == 'false':
            print("Tables NOT visible in TABLES and MAPS: " + table.get('name') + ": " + table.get('title'))
            notFound= False
        if table.get('Visible') == 'true' and table.get('VisibleInMaps') == 'false':
            print("Tables ONLY visible in TABLES: " + table.get('name') + ": " + table.get('title'))
            notFound= False
        if table.get('Visible') == 'false' and table.get('VisibleInMaps') == 'true':
            print("Tables ONLY visible in MAPS: " + table.get('name') + ": " + table.get('title'))
            notFound= False

    if (notFound):
        print("INFO: All tables are visible in tables and maps.")

    print('INFO: Test 11 completed..')
if __name__ == "__main__":
    run_test_11()
