
import warnings

from gherkan.containers.NLPModelManager import NLPModelManager
from gherkan.decoder.SignalParser import SignalParser
from gherkan.encoder.SignalFileWriter import SignalFileWriter


def signal_to_negated_signal(input_file_path: str, nmm: NLPModelManager):
    """
    Processes a signals file and saves it as NL file.

    Parameters
    ----------
    input_file_path path to signals file

    """

    # TODO find a better way to do this
    if input_file_path.endswith("_signals.feature"):
        output_file = input_file_path.replace("_signals.feature", "_neg_signals.feature")
    else:
        output_file = input_file_path + "_neg_signals.feature"

    # parse the signals file
    sp = SignalParser()
    sp.setNegateSignal()
    signalBatch = sp.parseFile(input_file_path)

    # save the NL file
    signalFileWriter = SignalFileWriter(nmm)
    signalFileWriter.encode(signalBatch, no_processing=True)
    signalFileWriter.write(output_file)

    return output_file