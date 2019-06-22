from openProduction.common import Exceptions

class TestClass:
    def __init__(self):
        pass
    
    def installRunner(self, runner):
        return True
    
    def install(self, suite):
        return True
    
    def assertEqual(self, val, comp, msg=None):
        if val != comp:
            if msg == None:
                msg="Asserion error %s!=%s"%(str(val), str(comp))
            raise Exceptions.OpenProductionAssertionError(msg)

    def assertInRange(self, val, minRange, maxRange, msg=None):
        if val < minRange or val > maxRange:
            if msg == None:
                msg="Asserion error %s!=[%s...%s]"%(str(val), str(minRange), str(maxRange))
            raise Exceptions.OpenProductionAssertionError(msg)

    def assertNotEqual(self, val, comp, msg=None):
        if val == comp:
            if msg == None:
                msg="Asserion error %s==%s"%(str(val), str(comp))
            raise Exceptions.OpenProductionAssertionError(msg)
