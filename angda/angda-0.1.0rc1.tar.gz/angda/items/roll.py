'''
Class definition for 'Roll'.
'''

class Roll:
    '''
    A single historical roll of a Dice.
    '''

    def __init__(self, roll, plus, steps):
        '''
        Initialise a new Roll.
        '''

        self.roll  = int(roll)
        self.plus  = int(plus or 0)
        self.steps = [int(step) for step in steps or [roll]]

    def __contains__(self, step):
        '''
        Return True if the Roll contains a step.
        '''

        return int(step) in self.steps

    def __eq__(self, roll):
        '''
        Return True if the Roll is equal to a Roll.
        '''

        return all(
            getattr(self, attr) == getattr(roll, attr, None)
            for attr in ['roll', 'plus', 'steps']
        )

    def __int__(self):
        '''
        Return the Roll as an integer.
        '''

        return self.roll

    def __iter__(self):
        '''
        Yield each step in the Roll.
        '''

        yield from self.steps

    def __len__(self):
        '''
        Return the number of steps in the Roll.
        '''

        return len(self.steps)

    def __repr__(self):
        '''
        Return the Roll as a code-representative string.
        '''

        return f'Roll({self.roll!r}, {self.plus!r}, {self.steps!r})'

    def __str__(self):
        '''
        Return the Roll as a string.
        '''

        return str(self.roll)
