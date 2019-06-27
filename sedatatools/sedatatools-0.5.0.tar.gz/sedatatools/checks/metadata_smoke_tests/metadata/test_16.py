import xml.etree.ElementTree as ET

def run_test_16(inputXML):
    # Check if source and publisher are all set
    print('INFO: Test 16 started..')
    notFound=True

    surveydatasets = inputXML.findall('SurveyDatasets/SurveyDataset')

    root = inputXML.getroot()

    if root.get('publisher') == '':
        print("ERROR: Publisher for the survey " + root.get('DisplayName') + " not set.")
        notFound= False

    # if (notFound):
    #     print("INFO: Publisher for the survey " + root.get('DisplayName') + " set.")

    for publish in surveydatasets:
        if publish.get('publisher') == '':
            print("ERROR: Publisher for the survey dataset " + publish.get('DisplayName') + " not set.")
            notFound= False

    # if (notFound):
    #     print("INFO: Publisher for the survey datasets " + publish.get('DisplayName') + " set.")

    for source in surveydatasets:
        if source.get('source') == '':
            print("ERROR: Source for the survey dataset " + source.get('DisplayName') + " not set.")
            notFound= False

    if (notFound):
        print("INFO: Publisher and source are all set.")



    print('INFO: Test 16 completed..')
if __name__ == "__main__":
    run_test_16()
