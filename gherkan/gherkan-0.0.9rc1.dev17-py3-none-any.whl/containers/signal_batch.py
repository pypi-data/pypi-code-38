from .signal_scenario import SignalScenario


class SignalBatch():
    """
    Container class for batch of test scenarios encoded into signals.

    ...

    Attributes
    ----------

    language : str
        language abbreviation (e.g. "cs" or "en") to indicate the language of the text

    name : str
        name of the batch (can be the same as filename)

    filename : str
        name of the original filename from which was the batch loaded (if available)

    desc : str
        description and/or precondition of the batch

    context : str
        context for the "while" conditions of the included text scenarios (i.e. a condition that will apply to all scenarios)

    scenarios : list
        list of SignalScenario objects that are part of this batch
    """

    def __init__(self, language=None, name="", filename="", desc="", context=""):
        self.language = language
        self.name = name
        self.filename = filename
        self.desc = desc
        self.context = context
        self.scenarios = []

    @property
    def filename(self):
        return self.__filename

    @filename.setter
    def filename(self, filename):
        self.__filename = filename
        if not self.name:
            self.name = filename

    def addScenario(self, scenario: SignalScenario):
        self.scenarios.append(scenario)
