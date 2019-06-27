def run_test_10(inputXML):
    # Lists variables where aggregation methods do not match (Original and SE variables)
    print('INFO: Test 10 started..')
    notFound=True
    for variable in inputXML.findall("SurveyDatasets/SurveyDataset[@abbreviation='ORG']/tables/table/variable"):
        org_var = variable.get('name')
        org_var_val = org_var + '.Value'
        org_method =variable.get('aggMethod')

        list_agg = filter(lambda x: org_var_val in x.get('FormulaFunctionBodyCSharp'), inputXML.findall("SurveyDatasets/SurveyDataset[@abbreviation='SE']/tables/table/variable"))
        for var_se in list_agg:
         se_var_name = var_se.get('name')
         se_var_method = var_se.get('aggMethod')
         if se_var_method != org_method:
          notFound= False
          print("WARNING: Agg.methods do not match for same variables: ORG: " + org_var + ' SE: ' + se_var_name)

    if (notFound):
         print ("INFO: All aggregation methods for variables match.")

    print('INFO: Test 10 completed..')

if __name__ == "__main__":

    run_test_10()
