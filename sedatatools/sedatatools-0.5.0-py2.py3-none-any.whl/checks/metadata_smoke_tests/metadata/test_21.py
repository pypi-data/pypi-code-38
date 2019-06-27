def run_test_21(inputXML):
    print('INFO: Test 21 started..')
    # check if full coverage is checked
    notFound=True

    for variable in inputXML.findall('geoTypes/geoType'):
        if variable.get('fullCoverage')== 'false':
            print("WARNING: FULL COVERAGE for " + variable.get('Name') + ": " + variable.get('Label') + " in Geo Types not checked.")
            notFound= False

    if (notFound):
        print("INFO: Full coverage for all the geo types is checked.")

    print('INFO: Test 21 completed..')
if __name__ == "__main__":
    run_test_21()
