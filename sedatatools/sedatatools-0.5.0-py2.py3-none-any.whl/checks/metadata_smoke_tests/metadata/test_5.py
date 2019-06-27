def run_test_5(inputXML):
    # Lists variables without Full labels

    print('INFO: Test 5 started..')
    notFound=True

    for variable in inputXML.findall("SurveyDatasets/SurveyDataset[@Visible='true']/tables/table/variable"):
     if not variable.get('qLabel'):
            print("ERROR: Variable with no Full label: " + variable.get('GUID') + ' ' + variable.get('label'))
            notFound= False

    if (notFound):
        print("INFO: All variables have full label entered.")
    print('INFO: Test 5 completed..')

if __name__ == "__main__":

     run_test_5()