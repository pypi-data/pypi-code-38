import os
from random import randint
from quotly.Quote import Quote


class Quoty:
    def __init__(self):
        self.quotes = []
        self.quotes_file = 'data/quotes'

        if not os.path.exists('data'):
            os.mkdir('data')

        if os.path.exists('.env'):
            print('> Start reading existing quotes')
            self.read_quotes()

            print('> Finished reading existing quotes. Found {0} quotes!'.format(len(self.quotes)))
            print('> Quotly is ready for action!')

    def get_random(self):
        if len(self.quotes) > 0:
            return self.quotes[randint(0, len(self.quotes) - 1)]

        return Quote("Sorry! No quotes found :(")

    def write_quotes(self):
        with open(self.quotes_file, 'w') as file:
            for q in self.quotes:

                ts = ""
                for t in q.targets:
                    ts += '{0},'.format(t)

                file.write('{0};{1}'.format(q.quote, ts))

    def read_quotes(self):
        try:
            if os.path.isfile(self.quotes_file):
                with open(self.quotes_file, 'r') as file:
                    content = file.readlines()

                content = [x.strip() for x in content]
                for l in content:
                    q = l.split(';')[0]
                    targets = l.split(';')[1].split(',')

                    self.quotes.append(Quote(q, targets))
        except FileNotFoundError:
            print('> Unable to read quotes file!')
