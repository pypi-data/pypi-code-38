"""

Application class that creates an instance of the STK11 application.


"""

from win32api import GetSystemMetrics
from comtypes.client import CreateObject

__author__ = "W. Conor McFerren"
__maintainer__ = "W. Conor McFerren"
__email__ = "cnmcferren@gmail.com"

class Application:
    def __init__(self):       
        """

        Application that holds the STK11 application.

        """
        self.__uiApplication = CreateObject("STK11.Application")
        self.__uiApplication.Visible = True #Make graphics visible
        self.__uiApplication.UserControl = True #Enable user control
        
        self.root = self.__uiApplication.Personality2
        
    def Connect(self, connectCommand):
        """
        
        Used to run STK Connect Commands
        
        Parameters:
            connectCommand (str): The string Connect Command.
        
        """
        self.root.ExecuteCommand(connectCommand)

    def Close(self):     
        """

        Closes the application.

       """

        self.__uiApplication.Quit()
