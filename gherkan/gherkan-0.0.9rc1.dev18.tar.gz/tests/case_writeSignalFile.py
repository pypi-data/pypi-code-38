from gherkan.decoder.NLParser import NLParser
from gherkan.encoder.SignalFileWriter import SignalFileWriter
import importlib
import os
from gherkan.containers.NLPModelManager import NLPModelManager

import gherkan.utils.constants as c

# Path to the text file with the signal batch
input_path = os.path.join(c.DATA_DIR, 'output')
output_path = os.path.join(c.DATA_DIR, 'output')
input_file = os.path.join(input_path, 'case_NLParser.feature')
output_file = os.path.join(output_path, 'case_NLParser_signals.feature')

nmm = NLPModelManager()
nmm.load_all_models()

nlFile = NLParser()
# Parse the entire file
nlBatch = nlFile.parseFile(input_file)

signalFileWriter = SignalFileWriter(nmm)
signalFileWriter.encode(nlBatch)
signalFileWriter.write(output_file)

with open(output_file, "rt", encoding="utf-8") as f:
    text = f.read()
    print(text)
