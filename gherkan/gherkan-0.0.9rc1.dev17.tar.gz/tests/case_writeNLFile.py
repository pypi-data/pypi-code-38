
import os
import gherkan.utils.constants as c
from gherkan.containers.NLPModelManager import NLPModelManager
from gherkan.flask_api.signal_to_nl import signal_to_nl

# Path to the text file with the signal batch

dir = os.path.join(c.DATA_DIR, 'output')
input_file = os.path.join(dir, 'case_SignalParser_signals.feature')

nmm = NLPModelManager()
nmm.load_all_models()

# saves automatically to file without the "_signals" suffix
signal_to_nl(input_file, nmm)

output_file = input_file.replace("_signals", "")

with open(output_file, "rt", encoding="utf-8") as f:
    text = f.read()
    print(text)
