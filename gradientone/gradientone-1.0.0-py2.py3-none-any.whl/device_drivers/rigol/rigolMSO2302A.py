from rigol_scope import RigolScope


class RigolMSO2302A(RigolScope):

    def __init__(self, command, instrument=None):
        super(RigolMSO2302A, self).__init__(command, instrument)
