def run_test_1(inputXML):
    # Lists variables with Unknown data type
    print('INFO: Test 1 started..')
    notFound=True
    for variable in inputXML.findall('SurveyDatasets/SurveyDataset/tables/table/variable'):
        if variable.get('dataType')== '1':
            print("ERROR: Variable with Unknown data type: " + variable.get('GUID'))
            notFound= False

    if (notFound):
        print("INFO: No variables found with Unknown data type.")
    print('INFO: Test 1 completed..')

if __name__ == "__main__":
    run_test_1()