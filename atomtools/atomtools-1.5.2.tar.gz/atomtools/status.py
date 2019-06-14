"""
status of calculations

running
error
complete
stopped


"""



from enum import Enum

class Status(Enum):
    complete = 0
    error = 1
    running = 2
    stopped = 3

    # def __repr__(


