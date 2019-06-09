import bisect
import enum


@enum.unique
class IntEnum(enum.IntEnum):
    @classmethod
    def make(cls, x):
        if isinstance(x, cls):
            return x

        if isinstance(x, str):
            return cls[x.upper().replace(' ', '_')]

        enums = sorted(cls)
        i = bisect.bisect_right(enums, x)
        return enums[i and i - 1]

    def pretty_string(self):
        return self.name.capitalize().replace('_', ' ')
