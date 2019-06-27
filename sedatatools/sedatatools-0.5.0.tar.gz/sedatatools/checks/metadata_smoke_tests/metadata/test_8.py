def run_test_8(inputXML):
    # Lists variables where data type does not match between original and SE tables
    print('INFO: Test 8 started..')
    notFound = True
    for variable in inputXML.findall("SurveyDatasets/SurveyDataset[@abbreviation='ORG']/tables/table/variable"):
        org_var = variable.get('name') + '.Value'
        org_type = variable.get('dataType')

        list_type = filter(lambda x: org_var in x.get('FormulaFunctionBodyCSharp'), inputXML.findall("SurveyDatasets/SurveyDataset[@abbreviation='SE']/tables/table/variable"))
        for var_se in list_type:
         se_var_name = var_se.get('name')
         se_var_type = var_se.get('dataType')
         if se_var_type != org_type:
          notFound = False
          print("WARNING: Data type does not match for this variable: ORG: " + org_var + ' SE: ' + se_var_name)

    if (notFound):
         print ("INFO: Data types for variables between SE and ORG match.")

    print('INFO: Test 8 completed..')

if __name__ == "__main__":

    run_test_8()


