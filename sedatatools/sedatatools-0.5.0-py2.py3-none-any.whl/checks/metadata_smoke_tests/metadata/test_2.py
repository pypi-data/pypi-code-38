def run_test_2(inputXML):
    print('INFO: Test 2 started..')
    # Lists variables with no formatting
    notFound=True
    for variable in inputXML.findall('SurveyDatasets/SurveyDataset/tables/table/variable'):
        if variable.get('formatting')== '0':
            print("ERROR: Variable with No formatting: " + variable.get('GUID'))
            notFound= False

    if (notFound):
        print("INFO: All variables have formatting set.")

    print('INFO: Test 2 completed..')
if __name__ == "__main__":
    run_test_2()
