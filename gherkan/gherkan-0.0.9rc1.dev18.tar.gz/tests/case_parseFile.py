import os

from gherkan.decoder.SignalParser import SignalParser
import gherkan.utils.constants as c

# Path to the text file with the signal batch
input_filename = os.path.join(c.DATA_DIR, 'input', 'test_R1NormalSequence_signals.feature')

# Load the file into a SignalFileLoader object
signalParser = SignalParser()
# Parse the entire file
signalBatch = signalParser.parseFile(input_filename)

# Print stuff related to the entire batch, read from the file
print("Showing signal batch from file {}".format(input_filename))
print("Batch name: {}".format(signalBatch.name))
print("Batch description: {}".format(signalBatch.desc))
print("Batch context condition: {}".format(signalBatch.context))
print("Used language: {}".format(signalBatch.language))

dir = os.path.join(c.DATA_DIR, 'output')

# parse the signals file
sp = SignalParser()
signalBatch = sp.parseFile(input_filename)

for scenario in signalBatch.scenarios:
    print("Scenario: {}\n".format(scenario.name))
    for statementListType in ["contextStatements", "givenStatements", "thenStatements", "whenStatements"]:
        statementList = getattr(scenario, statementListType)

        if statementList:
            print("\t{}\n".format(statementListType))

            for statement in statementList:
                print("\t{}".format(statement))

            print("\t------------")

