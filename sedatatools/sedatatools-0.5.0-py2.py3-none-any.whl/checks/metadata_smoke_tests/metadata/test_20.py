import xml.etree.ElementTree as ET

def run_test_20(inputXML):
    # check if cumulative tables are made for age and income tables
    print('INFO: Test 20 started..')

    notFound=True

    alltables = inputXML.findall('SurveyDatasets/SurveyDataset/tables/table')
    tables = ['Sex by Age', 'Age', 'Age (Detailed Version)', 'Household Income (In <DollarYear> Inflation Adjusted Dollars)', 'House Value for All Owner-Occupied Housing Units', 'House Value', 'Gross Rent (Housing Units With Cash Rent)', 'Gross Rent', 'Travel Time To Work for Workers 16 Years and Over (in 15 min intervals)', 'Travel Time To Work for Workers 16 Years and Over', 'Travel Time To Work']


    tabletitles = []
    for item in alltables:
        table_title= item.get('title')
        tabletitles.append(table_title)

    tabletitles2 = [table for table in tables if table in tabletitles]

    find_list = []
    for label in tabletitles2:
        item1 = label + " - Cumulative (Less)"
        item2 = label + " - Cumulative (More)"
        find_list.append(item1)
        find_list.append(item2)


    for title in find_list:
        if title not in tabletitles:
            print("WARNING: " + title + " does not exist.")
            notFound= False

    if (notFound):
        print("INFO: All tables were additional Cumulative tables needed are set.")


    print('INFO: Test 20 completed..')
if __name__ == "__main__":
    run_test_20()



