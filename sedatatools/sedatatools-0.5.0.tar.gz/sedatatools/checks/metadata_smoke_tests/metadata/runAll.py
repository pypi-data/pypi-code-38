import test_1, test_2, test_3, test_4, test_5, test_6, test_7, test_8, test_9, test_10, test_11, test_12, test_13, test_14, test_15, test_16, test_17, test_18, test_19, test_20, test_21
import xml.etree.ElementTree as ET
import sys

if len(sys.argv) != 3:
    print('ERROR: Enter metadata xml filename with full path as first argument.')
    print('ERROR: Enter test number or 0 to run all tests as second argument.')
    sys.exit(1)

def main(argv):
    inputFile = sys.argv[1]
    testArgument = sys.argv[2]

    print('BEGIN')
    if testArgument == '0':
        print('INFO: Running all tests...')
        # update max test number when adding a test
        maxTestNumber = 21
    else:
        print('INFO: Running single test...')
        maxTestNumber = 1

    while maxTestNumber > 0:
        testToRun =  str(maxTestNumber) if testArgument =='0' else testArgument
        print('INFO: Running Test ' + testToRun + ' for file ' + inputFile)
        inputXML = ET.parse(inputFile)
        getattr(globals()['test_'+ testToRun], 'run_test_' + testToRun)(inputXML)
        maxTestNumber = maxTestNumber-1


    print('END')
if __name__ == "__main__":
    main(sys.argv[1:])

