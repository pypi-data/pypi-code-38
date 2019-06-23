import inspect
from pprint import pprint

class Inspector():

    def print_vars(self, object=None):
        pprint(vars(object if object else self))

    # https://stackoverflow.com/questions/192109/is-there-a-built-in-function-to-print-all-the-current-properties-and-values-of-a
    def show_all_builtins(self):
        pprint(dir(__builtins__))

    def print_available_method(self, cls):
        results = self.inspect_method(cls)
        for m_info in results:
            print(m_info[0])


    def inspect_method(self, cls):
        return inspect.getmembers(cls, predicate=inspect.ismethod)

if __name__ == '__main__':
    i = Inspector()
    # i.show_all_builtins()
    i.print_available_method(i)
