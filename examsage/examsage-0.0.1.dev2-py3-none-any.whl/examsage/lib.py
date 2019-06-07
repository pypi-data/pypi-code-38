import random
import time

# "Create a Timing Context Manager" found at
# https://www.blog.pythonlibrary.org/2016/05/24/python-101-an-intro-to-benchmarking-your-code/
class timer():

    def __init__(self):
        self.start = time.time()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end = time.time()
        runtime = end - self.start
        msg = 'The function took {time} seconds to complete'
        print(msg.format(time=runtime))

"""
Example Call:
with timer():
    for i in range(10**7):
        kwargs_to_tex(onlyA = 5, onlyB = 10, AB = 15, notAB = 20)

Outputs:
The function took 34.583415031433105 seconds to complete
"""