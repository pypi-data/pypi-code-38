import re

def run_test_15(inputXML):
    # Check if the basic exceptions for title case are set: and, or, with, for, per, in, on, at, by, of, from, the, as, a, US, EU, GNI, GDP, PPP, IMF, DAC, FDI
    print('INFO: Test 15 started..')
    notFound=True
    inputNode = inputXML.findall("SurveyDatasets/SurveyDataset[@Visible='true']/tables/table/variable")
    inputNode2 = inputXML.findall("SurveyDatasets/SurveyDataset[@Visible='true']/tables/table")

    for table in inputNode2:
        skipList = ['and', 'or', 'with', 'for', 'per', 'in', 'on', 'at', 'by', 'of', 'from', 'the', 'as', 'a', 'to', 'than', 'est', 'over']
        skipList2 = ['US', 'EU', 'GNI', 'GDP', 'PPP', 'IMF', 'DAC', 'FDI', 'CPIA', 'IDA', 'PPG', 'IBRD', 'DIS', 'COM', 'INT', 'PNG', 'NFL', 'IAEA', 'UN', 'UNECE', 'UNPBF', 'WHO', 'TDS', 'DAC', 'LCU', 'US$', 'IFAD', 'UNAIDS', 'UNICEF', 'UNHCR', 'UNDP', 'UNFPA', 'UNRWA', 'UNTA', 'WFP', 'BOP', 'ARI', 'WEF']
        #exclude numbers and special characters
        tabletitle = re.sub(r'[^a-zA-Z ]',r'',table.get('title'))
        #tabletitle = ''.join([i for i in tabletitle if not i.isdigit()])
        tabletitle = tabletitle.split()

        for titles in tabletitle:
            if titles not in skipList and titles not in skipList2 and titles != '-':
                if titles.lower() in tabletitle or titles.upper() in tabletitle:
                    print("ERROR: Table " + table.get('name') + " in " + table.get('title') + " table title, the word " + titles + " is not set to Title Case.")
                    notFound= False

        for title1 in skipList:
            if title1.upper() in tabletitle or title1.title() in tabletitle:
                print("ERROR: Table " + table.get('name') + " " + table.get('title') + " has wrong exception case.")
                notFound= False

        for title2 in skipList2:
            if title2.lower() in tabletitle or title2.title() in tabletitle:
                print("ERROR: Table " + table.get('name') + " " + table.get('title') + " has wrong exception case.")
                notFound= False

    for variable in inputNode:
        skipList = ['and', 'or', 'with', 'for', 'per', 'in', 'on', 'at', 'by', 'of', 'from', 'the', 'as', 'a', 'to', 'than', 'est', 'only']
        skipList2 = ['US', 'EU', 'GNI', 'GDP', 'PPP', 'IMF', 'DAC', 'FDI', 'CPIA', 'IDA', 'PPG', 'IBRD', 'DIS', 'COM', 'INT', 'PNG', 'NFL', 'IAEA', 'UN', 'UNECE', 'UNPBF', 'WHO', 'TDS', 'DAC', 'LCU', 'US$', 'IFAD', 'UNAIDS', 'UNICEF', 'UNHCR', 'UNDP', 'UNFPA', 'UNRWA', 'UNTA', 'WFP', 'BOP', 'ARI', 'WEF']
        #exclude numbers and special characters
        labeltext = re.sub(r'[^a-zA-Z ]',r'',variable.get('label'))
        #labeltext = ''.join([i for i in labeltext if not i.isdigit()])
        labeltext = labeltext.split()


        for word in skipList:
            if word.upper() in labeltext[1:] or word.title() in labeltext[1:]:
                print("ERROR: Variable " + variable.get('name') + " " + variable.get('label') + " has wrong exception case.")
                notFound= False

        for word2 in skipList2:
            if word2.lower() in labeltext or word2.title() in labeltext:
                print("ERROR: Variable " + variable.get('name') + " " + variable.get('label') + " has wrong exception case.")
                notFound= False


    if (notFound):
        print("INFO: All exceptions for variable and table titles are set.")

    print('INFO: Test 15 completed..')
if __name__ == "__main__":
    run_test_15()
