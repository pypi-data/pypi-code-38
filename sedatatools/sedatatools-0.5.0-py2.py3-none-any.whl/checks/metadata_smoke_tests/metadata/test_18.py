def run_test_18(inputXML):
    # Lists variables with Aggregation method None
    print('INFO: Test 18 started..')
    notFound=True

    parent = inputXML.findall('SurveyDatasets/SurveyDataset/tables/table')

    for table in parent:
        if table.findall('OutputFormat')[0].get('TableTitle') != "":
            print("WARNING ON SIDE BY SIDE TABLE TITLE: " + table.findall('OutputFormat')[0].get('TableTitle') + " is the default TABLE TITLE for " + table.get('displayName'))
        notFound= False

        if table.findall('OutputFormat')[0].get('TableUniverse') != "":
            print("WARNING ON SIDE BY SIDE UNIVERSE: " + table.findall('OutputFormat')[0].get('TableUniverse') + " is the default UNIVERSE for " + table.get('displayName'))
        notFound= False

    if (notFound):
        print("INFO: No captions for tables found.")


    print('INFO: Test 18 completed..')
if __name__ == "__main__":
    run_test_18()
