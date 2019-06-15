'''
Top-level API functions.
'''

from angda.items import Dice

def roll(string, *, objects=False):
    '''
    Return the result of a Dice roll.
    '''

    dice = Dice.parse(string)
    roll = dice.roll()

    if objects:
        return {'dice': dice, 'roll': roll}
    else:
        return roll.roll
