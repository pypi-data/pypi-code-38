def run_test_7(inputXML):
    from collections import defaultdict
    # Lists variables with Unknown data type
    print('INFO: Test 7 started..')
    notFound = True
    # List that where all variable GUIDs will be stored
    guids_all = list()
    for variable in inputXML.findall('SurveyDatasets/SurveyDataset/tables/table/variable'):
        var_guid = variable.get('GUID')
        guids_all.append(var_guid)
    for table in inputXML.findall('SurveyDatasets/SurveyDataset/tables/table'):
        tab_guid = table.get('GUID')
        guids_all.append(tab_guid)

    duplicates = [item for item in set(guids_all) if item in guids_all[guids_all.index(item)+1:]]

    if len(duplicates) == 0:
        print("INFO: There are no duplicated variable and table GUIDs")
    else:
        print('These GUIDs are duplicated:')
        print(duplicates)

    print('INFO: Test 5 completed..')
if __name__ == "__main__":
     run_test_7()







































def run_test_6(inputXML):

 # Lists tables with duplicate table GUID

 print('INFO: Test 6 started..')

 notFound=True
 chunks = []

 for table in inputXML.findall('SurveyDatasets/SurveyDataset/tables/table'):
  guid =table.get('GUID')
  chunks.append(guid)


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




