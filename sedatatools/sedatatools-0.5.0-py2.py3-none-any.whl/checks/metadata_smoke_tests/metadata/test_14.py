import utils as u
def run_test_14(inputXML):
    # List variables where variable label is rate, percentage, dollars, minutes, min, gross rent and similar and its formatting.
    print('INFO: Test 14 started..')
    notFound=True
    for variable in inputXML.findall('SurveyDatasets/SurveyDataset/tables/table/variable'):
        conds = ['rate', 'percent', 'percentage', 'dollar', 'dollars', 'min', 'minutes', 'rent', 'income', 'quintile']
        labeltext = variable.get('label').lower().split(' ')
        for cond in conds:
            if (cond in labeltext):
                print("INFO: Variable " + variable.get('name') + ": " + variable.get('label') + " is formatted as " + u.getFormats(variable.get('formatting')))
                notFound= False

    if (notFound):
        print("INFO: No rates, percentages, income, and similar variable labels found.")

    print('INFO: Test 14 completed..')
if __name__ == "__main__":
    run_test_14()
