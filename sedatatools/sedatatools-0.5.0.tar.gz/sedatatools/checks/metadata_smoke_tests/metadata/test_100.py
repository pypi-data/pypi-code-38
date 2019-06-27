

def run_test_100(inputXML):
   notFound=True
   for variable in inputXML.findall('SurveyDatasets/SurveyDataset/tables/table/variable'):
       conds = ["Rate", "Percent", "Percentage", "dollars", "dollar", "minutes", "min", "gross", "rent", "income"]
       for word in conds:
           e = variable.get('label')
           if word in variable.get('label'):
               print("INFO: Variable " + variable.get('name') + ": " + variable.get('label') + " is formatted as " + variable.get('formatting'))
               notFound= False

   if (notFound):
       print("INFO: No rates, percentages, income, and similar variable labels found.")