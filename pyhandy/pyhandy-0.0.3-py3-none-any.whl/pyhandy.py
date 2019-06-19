'''
File:          pyhandy.py
File Created:  Wednesday, 19th June 2019 5:49:40 pm
Author:        xss (callmexss@126.com)
Description:   handy python tools to make my life easier
-----
Last Modified: Wednesday, 19th June 2019 6:00:06 pm
Modified By:   xss (callmexss@126.com)
-----
'''
import random


class RandomWorker:
    """A worker who generate random things."""

    def __init__(self, rand=None):
        """Construct a RandomWorker
        
        Arguments:
            rand {random.Random} -- an instance of random.Random class
        """
        self.rand = rand if rand else random.Random()

    def gen_list(self, size=10, scope=(-100, 100), duplicated=False,
                 etype=int):
        """Generate a random list.
        
        Keyword Arguments:
            size {int} -- the length of the list (default: {10})
            scope {tuple} -- the scope of the elements (default: {(-100, 100)})
            duplicated {bool} -- unique or not (default: {False})
            etype {[type]} -- the type of elements (default: {int})
        
        Returns:
            list -- a random generated list
        """
        random = self.rand
        start, end = scope
        if size > (end - start) and not duplicated:
            raise ValueError(
                f"The size `{size}` is larger than the given scope `{scope}` "
                "to generate a unique random list.")

        if duplicated:
            ret = [random.randint(start, end) for count in range(size)]
        else:
            ret = random.sample(range(start, end), size)

        if etype is int:
            return ret
        elif etype is float:
            return [random.random() * x for x in ret]


if __name__ == '__main__':
    worker = RandomWorker()
    li = worker.gen_list(100, (1, 10), etype=float, duplicated=True)
    print(li)