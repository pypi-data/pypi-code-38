import xml.etree.ElementTree as ET

def run_test_17(inputXML):
    # Check if survey name inserted into the data categories
    print('INFO: Test 17 started..')
    notFound=True

    surveydatasets = inputXML.findall('SurveyDatasets/SurveyDataset/tables/table')

    root = inputXML.getroot()

    for category in surveydatasets:
        categories = category.get('DataCategories').split(';')
        for categ in categories:
            if categ == root.get('DisplayName') or categ == root.get('name'):
                print("ERROR: Table " + category.get('displayName') + ": " + category.get('title') + " contains survey name in Data Category. Please make sure to remove it.")
                notFound= False

    if (notFound):
        print("INFO: Survey name is not inserted into the data categories.")



    print('INFO: Test 17 completed..')
if __name__ == "__main__":
    run_test_17()
