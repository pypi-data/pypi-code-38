'''
Class definition for 'Dice'.
'''

from angda.items.roll import Roll
from angda.tools      import nota
from angda.tools      import rand

class Dice:
    '''
    A random rollable dice.
    '''

    def __init__(self, dice, size, plus=None):
        '''
        Initialise a new Dice.
        '''

        self.dice  = int(dice)
        self.size  = int(size)
        self.plus  = int(plus or 0)
        self.rolls = []

    @classmethod
    def parse(cls, string):
        '''
        Return a new Dice from a parsed notation string.
        '''

        data = nota.parse(string)
        return cls(data['dice'], data['size'], data['plus'])

    def __eq__(self, dice):
        '''
        Return True if the Dice is equal to a Dice.
        '''

        return all(
            getattr(self, attr) == getattr(dice, attr, None)
            for attr in ['dice', 'size', 'plus']
        )

    def __iter__(self):
        '''
        Yield every Roll in the Dice.
        '''

        yield from self.rolls

    def __repr__(self):
        '''
        Return the Dice as a code-representative string.
        '''

        return f'Dice({self.dice!r}, {self.size!r}, {self.plus!r})'

    def __str__(self):
        '''
        Return the Dice as a string.
        '''

        base = f'{self.dice}d{self.size}'
        plus = f'+{self.plus}' if self.plus else ''
        return base + plus

    def roll(self):
        '''
        Generate a new Roll, store it, and return it.
        '''

        steps = rand.integers(1, self.size, self.dice)
        total = sum(steps) + self.plus
        roll  = Roll(total, self.plus, steps)
        self.rolls.append(roll)
        return roll
