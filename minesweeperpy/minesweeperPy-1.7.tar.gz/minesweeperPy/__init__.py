"""
minesweeperPy 1.7
The minesweeper generator in Python 3
Made by Steven Shrewsbury Dev. (AKA: stshrewsburyDev)
"""

import random


__title__ = 'minesweeperPy'
__author__ = 'stshrewsburyDev'
__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2019 stshrewsburyDev'
__version__ = '1.7'
__URL__ = "https://github.com/stshrewsburyDev/minesweeperPy"

__changeLogs__ = """
 - The entire module has been rewritten with slightly cleaner code
 - Function and class names have been changed, use help(minesweeperPy) to see the new names
 - __version__ __title__ __author__ __licence__ __copyright__ __URL__ and __changeLogs__ added to see more info on the module
 - As well as blank cell identifiers there are now mine cell identifiers
 - preGenerate() added to quickly generate a grid using one of the four built in presets
"""

preGameLevels = ["easy", "medium", "hard", "expert"]

preGamePresets = {
    "easy": {
        "gridSizeX": 9,
        "gridSizeY": 9,
        "mines": 10
    },
    "medium": {
        "gridSizeX": 16,
        "gridSizeY": 16,
        "mines": 40
    },
    "hard": {
        "gridSizeX": 25,
        "gridSizeY": 20,
        "mines": 100
    },
    "expert": {
        "gridSizeX": 50,
        "gridSizeY": 30,
        "mines": 200
    }
}

class mineGen():
    def __init__(self,
                 gridSizeX: int=0, gridSizeY: int=0,
                 blankIdentifier=" ",
                 mineIdentifier="M"):
        """
        Makes the main generator object using minesweeperPy.mineGen(gridSizeX, gridSizeY, blankIdentifier)
        :param gridSizeX: integer above 4
        :param gridSizeY: integer above 4
        :param blankIdentifier: string, default will be " "
        :param mineIdentifier: string, default will be "M"
        """
        if gridSizeX <= 4 or gridSizeY <= 4:
            raise ValueError("""Error in mineGen()
Expected:
    - gridSizeX = 5+
        got {0}
    - gridSizeY = 5+
        got {1}""".format(gridSizeX,
                       gridSizeY))

        if blankIdentifier is None or mineIdentifier is None:
            raise TypeError("""Error in mineGen()
Expected:
    - blankIdentifier = string
        got {0}
    - mineIdentifier = string
        got {1}""".format(blankIdentifier,
                          mineIdentifier))

        self.gridSizeX = gridSizeX
        self.gridSizeY = gridSizeY
        self.blankIdentifier = blankIdentifier
        self.mineIdentifier = mineIdentifier
        self.gridContents = [self.mineIdentifier, self.blankIdentifier, "1", "2", "3", "4", "5", "6", "7", "8"]

    def generateGrid(self, mineCount: int=0):
        """
        Generate a new minesweeper grid using the mine generator settings
        :param mineCount: integer 0 or above
        :return: JSON library
            format of JSON:
                {
                  "grid": list of grid,
                  "blankIdentifier": the blank identifier used,
                  "mineIdentifier": the mine identifier used
                }
        """
        if mineCount <= -1: # If the mine count is under 0
            raise ValueError("""Error in generateGrid()
Expected:
    - mineCount = 0+
        got {}""".format(mineCount))
        if mineCount >= (self.gridSizeY * self.gridSizeX)+1:
            raise ValueError("""Error in generateGrid()
Expected:
    - mineCount = 0 - {0}
        got {1}""".format((self.gridSizeY * self.gridSizeX),
                          mineCount))

        returnOutput = {}
        grid = []

        # Make the list of areas to place the mines, done before creating the grid so mine overlapping doesn't occur
        tempMineLocations = []
        for mine in range (0, mineCount): # For each mine that needs to be added
            mineSelected = False # Set a temp boolean to test for a working mine location
            while not mineSelected: # While a mine has not been selected
                mineLocation = [random.randint(0, self.gridSizeX-1),
                                random.randint(0, self.gridSizeY-1)] # Generate a new location
                if mineLocation not in tempMineLocations: # If that mine location hasn't been taken
                    tempMineLocations.append(mineLocation) # Add the new mine location to the mine locations list
                    mineSelected = True # Stop the mine selection for this mine
                # else: It will continue selecting new locations until an available slot is found


        # Generate 2D list grid
        for row in range(0, self.gridSizeY):
            rowContent = [] # The row list that will be added to the grid list later
            for column in range(0, self.gridSizeX): # Each cell in a row
                if [column, row] in tempMineLocations: # If the cell is a mine
                    rowContent.append(self.mineIdentifier) # Set the cell to the mine identifier if set, if none set it will use default "M"
                else:
                    nearMineCount = 0 # The number for mines around the cell 1-8, blank if none
                    # Check for each cell around the cell to test for a mine, if a mine is found 1 is added to the
                    # mine count

                    if [column+1, row] in tempMineLocations:
                        nearMineCount += 1
                    if [column-1, row] in tempMineLocations:
                        nearMineCount += 1
                    if [column, row+1] in tempMineLocations:
                        nearMineCount += 1
                    if [column, row-1] in tempMineLocations:
                        nearMineCount += 1
                    if [column+1, row+1] in tempMineLocations:
                        nearMineCount += 1
                    if [column+1, row-1] in tempMineLocations:
                        nearMineCount += 1
                    if [column-1, row+1] in tempMineLocations:
                        nearMineCount += 1
                    if [column-1, row-1] in tempMineLocations:
                        nearMineCount += 1

                    if nearMineCount == 0: # If there are no mines around this cell
                        rowContent.append(self.blankIdentifier) # Set the cell to the blank identifier if set, if none set it will use default " "
                    else:
                        rowContent.append("{}".format(nearMineCount)) # Set the cell to the number of mines found around the cell

            grid.append(rowContent) # Add the generated row to the grid

        # Set up the return output for the function
        # Uses JSON format structure:
        #   {
        #       "grid": list of grid,
        #       "blankIdentifier": the blank identifier used,
        #       "mineIdentifier": the mine identifier used
        #   }
        returnOutput["grid"] = grid
        returnOutput["blankIdentifier"] = self.blankIdentifier
        returnOutput["mineIdentifier"] = self.mineIdentifier

        # Return the finished result
        return returnOutput

def gridInfo(grid=None, blankIdentifier=None, mineIdentifier=None):
    """
    Shows the information about a grid generation
    :param grid: 2D list of a grid
    :param mineIdentifier: string of the mine identifier in the grid
    :param blankIdentifier: string of the blank identifier in the grid
    :return: JSON library
        format of JSON:
            {
              "gridColumns": number of columns in the grid,
              "gridRows": number of rows in the grid,
              "mineCount": number of mine cells in the grid,
              "nonMineCells": number of non mine cells in the grid,
              "emptyCells": number of empty cells in the grid,
              "numberedCells": number of numbered cells in the grid
            }
    """
    if not isinstance(grid, list): # If the grid is a list
        raise TypeError("""Error in gridInfo()
Expected:
    - grid = list of grid
        got type {}""".format(type(grid))) # Raise this problem as an error

    if blankIdentifier is None or mineIdentifier is None: # If the blankIdentifier or mineIdentifier is set to default
        raise TypeError("""Error in gridInfo()
Expected:
    - blankIdentifier = the term used for the blank cell identifier in the grid
        got {0}
    - mineIdentifier = the term used for the mine cell identifier in the grid
        got {1}""".format(blankIdentifier,
                          mineIdentifier)) # Raise this problem as an error

    gridInfo = {
        "gridColumns": len(grid[0]),
        "gridRows": len(grid),
        "mineCount": 0,
        "nonMineCells": 0,
        "emptyCells": 0,
        "numberedCells": 0,
        "NOTICE": "If these results seem wrong re-run gridInfo() with the correct mine and blank cell identifiers"
    } # Set up the gridInfo with the known info

    for row in grid: # For each row in the grid
        for cell in row: # For each cell in the row
            if cell == mineIdentifier: # If the cell is a mine
                gridInfo["mineCount"] += 1 # Update the grid info

            elif cell == blankIdentifier: # If the cell is a blank one
                gridInfo["emptyCells"] += 1 # Update the grid info
                gridInfo["nonMineCells"] += 1  # Update the grid info

            else: # This only runs mainly if its a number cell
                gridInfo["numberedCells"] += 1 # Update the grid info
                gridInfo["nonMineCells"] += 1  # Update the grid info

    return gridInfo # Return the gridInfo

def preGenerate(level=None,
                blankIdentifier=" ",
                mineIdentifier="M"):
    """
    Pre generates a one time mine using a level preset
    :param level: string level (easy, medium, hard, expert)
    :param blankIdentifier: string, default will be " "
    :param mineIdentifier: string, default will be "M"
    :return: JSON library
        format of JSON:
            {
              "grid": list of grid,
              "blankIdentifier": the blank identifier used,
              "mineIdentifier": the mine identifier used
            }
    """
    levelLower = str(level).lower()

    if levelLower not in preGameLevels:
        raise TypeError("""Error in preGenerate()
Expected:
    - level = string of level type (easy, medium, hard, expert)
        got {}""".format(levelLower))

    if blankIdentifier is None or mineIdentifier is None:
        raise TypeError("""Error in preGenerate()
Expected:
    - blankIdentifier = string
        got {0}
    - mineIdentifier = string
        got {1}""".format(blankIdentifier,
                          mineIdentifier))

    grid = mineGen(gridSizeX=preGamePresets[levelLower]["gridSizeX"],
                   gridSizeY=preGamePresets[levelLower]["gridSizeY"],
                   blankIdentifier=blankIdentifier,
                   mineIdentifier=mineIdentifier).generateGrid(mineCount=preGamePresets[levelLower]["mines"])

    return grid