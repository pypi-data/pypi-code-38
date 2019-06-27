def run_test_12(inputXML):
    # List of filter rule and data categories by table and variable
    print('INFO: Test 12 started..')
    notFound=True
    for table in inputXML.findall('SurveyDatasets/SurveyDataset/tables/table'):
        if table.get('DataCategories')!= '':
            print("List of DATA CATEGORIES: Data Category in " + table.get('name') + ": " + table.get('title') + " is: " + table.get('DataCategories'))

            notFound= False

    if (notFound):
        print("INFO: No DATA CATEGORIES found in TABLES. Please make sure to add them.")


        if table.get('FilterRuleName')!= '':
            print("List of TABLE Filter Rules: Filter Rule in " + table.get('name') + ": " + table.get('title') + " is: " + table.get('FilterRuleName'))

            notFound= False

    if (notFound):
        print("INFO: No FILTER RULES found in TABLES. Please make sure to add them.")

    for variable in inputXML.findall('SurveyDatasets/SurveyDataset/tables/table/variable'):
        if variable.get('FR')!= '':
            print("List of VARIABLE Filter Rules: Filter Rule in " + variable.get('name') + ": " + variable.get('label') + " is: " + variable.get('FR'))

            notFound= False

    if (notFound):
        print("INFO: No FILTER RULES found in VARIABLES. Please make sure that tables' filter rule do apply on all the variables within the table.")


    print('INFO: Test 12 completed..')
if __name__ == "__main__":
    run_test_12()

