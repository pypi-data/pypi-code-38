"""

Holds the scenario that that is added to the instance of the application.

Scenario holds the simulations and all objects within (such as satellites,
area targets, cameras, etc.).

"""
from win32api import GetSystemMetrics
from comtypes.client import CreateObject
from comtypes.gen import STKObjects
from comtypes import COMError

__author__ = "W. Conor McFerren"
__maintainer__ = "W. Conor McFerren"
__email__ = "cnmcferren@gmail.com"

class Scenario:

    def __init__(self, application, name, timePeriod):
        """

        Creates an instance of the scenario.

        Parameters:
            application (STK11 Instance): Running instance of STK 11.
            name (str): Name of the scenario to be created.
            timePeriod (str): The amount of time you want the scenario to run for.
                        Examples: "+24hr", "+365days", "+10days".

        """  
        
        self.__guardian = application
        self.name = name.replace(' ','_')
        
        application.root.NewScenario(self.name)
        self.__scenario = application.root.CurrentScenario
        self.__scenario = self.__scenario.QueryInterface(STKObjects.IAgScenario)
        try:
            self.__scenario.SetTimePeriod('Today',str(timePeriod))
        except COMError:
            raise ValueError, "Time period not properly formatted"

    def SetTimePeriod(self, elapsedTime):    
        """

        Sets a new time period for the scenario.

        Parameters:
            elapsedTime (str): The amound of time you want the scenario to run for.
                            Examples: "+24hr", "+365days", "+10days".

        """

        self.__scenario.SetTimePeriod('Today',str(elapsedTime))

    def GetReference(self):          
        """

        Gets the reference variable for the scenario.

        Returns:
            self.__scenario (STKObjects.IAgScenario): The currenting running scenario.
        
        """
        
        return self.__scenario
    
    def Close(self):     
        """

        Closes the scenario.

        """

        self.__guardian.root.CloseScenario()

    def GetGuardian(self):   
        """

        Returns the guardian of the scenario class, which is the application.
        
        Returns:
            self.__guardian (STK11 Instances): The running application.

        """
        return self.__guardian
