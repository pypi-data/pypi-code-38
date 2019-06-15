'''
Main program script.
'''

from angda.items import Dice
from angda.tools import clui

def main():
    '''
    Run the main Angda program.
    '''

    args = clui.parse()

    for num, string in enumerate(args['rolls']):
        num += 1

        try:
            dice = Dice.parse(string)
            roll = dice.roll()

        except ValueError as error:
            print(f'Error: {error}.')
            raise SystemExit

        if args['details']:
            print(f'- String: {dice!s}.')
            print(f'- Fields: Dice={dice.dice}, Size={dice.size}, Plus={dice.plus}.')
            print(f'- Result: {roll.steps} + {roll.plus} = {roll.roll}.\n')

        elif args['quiet']:
            print(roll.roll)

        else:
            print(f'#{num}: {string} = {roll.roll}.')


if __name__ == '__main__':
    main()
