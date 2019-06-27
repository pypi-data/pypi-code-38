def run_test_6(inputXML):

 # Lists tables with duplicate table GUID

    print('INFO: Test 6 started..')

    notFound=True
    chunks = []

    for table in inputXML.findall('SurveyDatasets/SurveyDataset/tables/table'):
        guid =table.get('GUID')
        chunks.append(guid)

 # For each element, check all following elements for a duplicate.
    for i in range(0, len(chunks)):
        for x in range(i + 1, len(chunks)):
            if chunks[i] == chunks[x]:
             print('Duplicate table GUID: ' + chunks[i])

            notFound= False

    if (notFound):
        print("INFO: No duplicate table GUIDs.")

    print('INFO: Test 6 completed..')

if __name__ == "__main__":
 run_test_6()



