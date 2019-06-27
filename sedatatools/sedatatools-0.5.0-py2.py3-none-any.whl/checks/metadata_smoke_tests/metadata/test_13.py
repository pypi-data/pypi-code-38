def run_test_13(inputXML):
    # Lists variables with Aggregation method None
    print('INFO: Test 13 started..')
    notFound=True
    for geotype in inputXML.findall('geoTypes/geoType'):
        if geotype.get('Label') == geotype.get('PluralName'):
            print("WARNING: GeoType with Label equal to PluralName: " + geotype.get('GUID') + ' ' + geotype.get('Name'))
            notFound= False

    if (notFound):
        print("INFO: No GeoTypes found with with Label equal to PluralName.")

    print('INFO: Test 13 completed..')
if __name__ == "__main__":
    run_test_13()
