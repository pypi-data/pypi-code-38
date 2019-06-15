class Init:
    """
    
    Used for the first time running stkhelper on a computer.
    
    """
    
    def __init__(self):
        try:
            from win32api import GetSystemMetrics
            from comtypes.client import CreateObject
        
            print("Creating STK11 Object...")
            uiApplication = CreateObject("STK11.Application")
            print("STK11 Objects successfully created.")
        
            uiApplication.Visible =False
            uiApplication.UserControl = False
        
            root = uiApplication.Personality2
            print("\nGen folder for STKUtil and STK Objects successfully created.")
        
            print("Terminating STK11...")
            uiApplication.Quit()
            print("Successful termination.")
            
        except Exception as e:
            print("Unsucessful initialization of STK11. Failure to set up " +
                  "gen folder for STKUtil and STK Objects." + 
                  "\n\n\tSTK ERROR:\n" + str(e))