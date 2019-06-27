def run_test_9(inputXML):
    # Geography Identifiers Data Type set to 'string'
    print('INFO: Test 9 started..')
    notFound=True
    for variable in inputXML.findall('GeoSurveyDataset/tables/table/variable'):
        if variable.get('dataType') != '2':
            print("ERROR: Geography Identifiers for " + variable.get('name') + " set to Data Type other than string.")
            notFound= False

    if (notFound):
        print("INFO: All Geography Identifiers Data Type set to string.")
    print('INFO: Test 9 completed..')

if __name__ == "__main__":
    run_test_9()