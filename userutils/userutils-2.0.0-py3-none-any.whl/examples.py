import userutils
from pprint import pprint


def say(what):
    print(what)


def json(msg):
    j = userutils.getJSON(msg, enforcedtype=dict, invalidtypemsg="Please enter a dictionary! ")
    print(f'We got a {type(j).__name__}: ')
    pprint(j)


hi = userutils.MenuItem('Say Hi', 'hi')
bye = userutils.MenuItem('Say Bye', 'bye')
j = userutils.CallbackMenuItem('Pretty print JSON', json, args=('Enter JSON: ',), choice='p')
quit = userutils.MenuItem('Quit', None, choice='q')

m = userutils.Menu(hi, bye, j, quit)


def main():
    if userutils.yesNo('Show the menu? ', loop=False):
        while True:
            item = m.show()

            if hasattr(item, 'value'):
                if item.value is None:  # the option was quit
                    break
                print(item.value)
    else:
        print('ok then bye')


if __name__ == '__main__':
    main()
