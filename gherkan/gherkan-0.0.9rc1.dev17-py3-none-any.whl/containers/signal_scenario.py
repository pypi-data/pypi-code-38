class SignalScenario():
    """
    Container class for test scenario encoded into signal.

    ...

    Attributes
    ----------

    name : str
        name of the scenario

    contextStatements : list
        context for the "given" conditions

    givenStatements : list
        list Given conditions

    whenStatements : list
        list When conditions

    thenStatements : list
        list Then conditions

    """

    def __init__(self, name=""):
        self.name = name
        self.contextStatements = []
        self.givenStatements = []
        self.whenStatements = []
        self.thenStatements = []
