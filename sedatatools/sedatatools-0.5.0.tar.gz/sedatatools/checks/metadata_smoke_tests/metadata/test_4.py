def run_test_4(inputXML):
    # check if database name is the same in all Db name parameters
    print('INFO: Test 4 started..')
    notFound=True
    counter=-1
    datasetsList = inputXML.findall('GeoSurveyDataset/datasets/dataset')
    for item in datasetsList:
        counter = counter+1
        currentDbName = item.get('DbName')
        for i in range(len(datasetsList)-counter, counter, -1):
        #for i, item in enumerate(datasetsList, start=len(datasetsList)-counter):
           element = datasetsList[i-1]
           nextDbName = element.get('DbName')
           if currentDbName != nextDbName:
                print("ERROR: Variables with different dbname: " + item.get("GeoTypeName") + " and " + element.get('GeoTypeName'))
                notFound= False

    if (notFound):
        print("INFO: No geo types found with different Db name.")

    print('INFO: Test 4 completed..')
if __name__ == "__main__":
    run_test_4()
