from typing import Iterable, Callable
from .closest import closest

def set_validator(valid_set:Iterable[str])->Callable:
    def wrapper(value:str)->bool:
        if value not in valid_set:
            candidate = closest(value, valid_set)
            if candidate:
                print("Given value {value} is not valid, did you mean {candidate}?".format(value=value, candidate=candidate))
            return False
        return True
    return wrapper