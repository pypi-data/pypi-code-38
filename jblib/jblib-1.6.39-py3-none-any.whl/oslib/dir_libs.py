import os

class cd:
    """
        Context manager for changing the current working directory 
        
        class cd()

        Example: 
            with cd(directory):
                print (os.getcwd()) 

            print (os.getcwd()) ## Moves you back to the originating directory on exit
    """
    def __init__(self, newPath):
        self.newPath = newPath   

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)