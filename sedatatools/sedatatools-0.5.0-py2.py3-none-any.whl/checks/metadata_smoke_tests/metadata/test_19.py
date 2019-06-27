import xml.etree.ElementTree as ET

def run_test_19(inputXML):
    # check if bracket values are set for age, income etc tables
    print('INFO: Test 19 started..')

    variable = inputXML.findall("SurveyDatasets/SurveyDataset[@Visible='true']/tables/table/variable")
    notFound=True

    for item in inputXML.findall('SurveyDatasets/SurveyDataset/tables/table/variable'):
        labeltext = item.get('label').split(' ')
        variablename = item.get('name')
        if any('Years' in item for item in labeltext) or any('$' in item for item in labeltext):
            exepctions = ['Female Population 15 Years and over:', 'Male Population 15 Years and over:']
            if variablename.find("_001") == -1 and variablename.find("s") == -1 and item.get('BracketFromVal') == "0" and item.get('BracketToVal') == "0" and item.get('label') not in exepctions:
                print("WARNING: " + item.get('name') + ": " + item.get('label') + " do not have BRACKET VALUE set.")
        notFound= False

    if (notFound):
        print("INFO: All bracket Values are set.")


    print('INFO: Test 19 completed..')
if __name__ == "__main__":
    run_test_19()



