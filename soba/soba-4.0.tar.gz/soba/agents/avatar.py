import random
import soba.agents.resources.aStar as aStar
import soba.agents.resources.fov as fov
import soba.visualization.ramen.performanceGenerator as ramen
from soba.agents.occupant import Occupant
import time

class Avatar(Occupant):
    """
    This class enables to create avatars that represent virtual occupants, that is, they are
    not controlled by the simulation but by an API Rest. However, certain important aspects 
    such as position in space inherit from the occupant class.

    Attributes:
        model: Simulation model.
        unique_id: Unique avatar identifier as an occupant.
        fov: List of positions (x, y) that the avatar can see.
        state: Current avatar state.
        pos: Current avatar position.
        color: Color of the avatar in the visualization.
        shape: Shape of the avatar in the visualization.
    
    Methods:
        getWay: Invocation of the AStar resource to calculate the optimal path.
        posInMyFOV: Check if a position is in my field of vision.
        makeMovementAvatar: Carry out a movement: displacement between cells.
        checkLeaveArrive: Notify the entrance and exit of the building by an occupying agent.
        getFOV: Calculation of the occupant's field of vision, registered in the attribute fov.
    
    """
    def __init__(self, unique_id, model, initial_pos, color = 'red', initial_state='walking'):

        self.model = model
        self.unique_id = unique_id
        self.fov = []
        self.state = initial_state
        self.pos = initial_pos
        self.model.grid.place_agent(self, initial_pos)
        self.color = color
        self.shape = 'circle'
        self.movement = {}        
        self.movements = [self.pos]
        self.inbuilding = False
        self.getFOV()

    def getWay(self, pos = None, pos_to_go = None, other = []):
        '''
        Invocation of the AStar resource to calculate the optimal path.
            Args:
                pos: Initial position, by default the current position of the occupant.
                pos_to_go: Final position, by default the value of the 'pos_to_go' attribute of the occupant.
                other: List of auxiliary positions given to be considered impenetrable by the occupants, 
                that is, they will not be used by the AStar.
            Return: List of positions (x, y).
        '''
        posSend = pos
        pos_to_goSend = pos_to_go
        if pos == None:
            posSend = self.pos
        if pos_to_go == None:
            pos_to_goSend = self.pos_to_go
        return aStar.getPathContinuous(self.model, posSend, pos_to_goSend, other)

    def posInMyFOV(self, pos):
        '''
        Check if the position is in my field of vision
            Args: 
                pos: Position to be checked
            Return: Boolean
        '''
        if pos in self.fov:
            return True
        return False

    def makeMovementAvatar(self, pos):
        '''
        Carry out a movement: displacement between cells.
            Args: 
                pos: Position to be moved.
        '''
        self.model.grid.move_agent(self, pos)
        self.reportMovement()
        self.movements = [self.pos]
        self.checkLeaveArrive()
        self.getFOV()

    def reportMovement(self):
        pass

    def checkLeaveArrive(self):
        """ Notify the entrance and exit of the building by an occupying agent. """
        if not self.inbuilding:
            if self.model.ramenAux:
                ramen.reportCreation(self, 'E')
            self.inbuilding = True
            return
        if (self.pos in self.model.exits) and self.inbuilding:
            self.inbuilding = False
            if self.model.ramenAux:
                ramen.reportExit(self)
            return

    def getFOV(self):
        '''Calculation of the occupant's field of vision, registered in the attribute fov'''
        asciMap = self.model.asciMap
        fovMap, flag = fov.makeFOV(asciMap, self.pos)
        self.fov = []
        for index1, line in enumerate(fovMap):
            for index2, element in enumerate(line):
                if element == flag:
                    self.fov.append((index2, index1))

    def step(self):
        return