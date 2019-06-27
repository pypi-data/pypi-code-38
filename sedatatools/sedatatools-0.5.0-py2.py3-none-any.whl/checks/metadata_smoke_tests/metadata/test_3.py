def run_test_3(inputXML):
    # Lists variables with Aggregation method None
    print('INFO: Test 3 started..')
    notFound=True
    for variable in inputXML.findall('SurveyDatasets/SurveyDataset/tables/table/variable'):
        if variable.get('AggregationStr')== 'None':
            print("ERROR: Variable with Aggregation method None: " + variable.get('GUID') + ' ' + variable.get('label'))
            notFound= False

    if (notFound):
        print("INFO: No variables found with Aggregation method None.")

    print('INFO: Test 3 completed..')
if __name__ == "__main__":
    run_test_3()
