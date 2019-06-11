from pprint import pprint

class Inspector():

    def print_vars(self, object=None):
        pprint(vars(object if object else self))

    # https://stackoverflow.com/questions/192109/is-there-a-built-in-function-to-print-all-the-current-properties-and-values-of-a
    def show_all_builtins(self):
        pprint(dir(__builtins__))

if __name__ == '__main__':
    i = Inspector()
    # i.show_all_builtins()
