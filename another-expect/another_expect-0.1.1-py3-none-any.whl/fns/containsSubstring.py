from .decorators.argIsType import argIsType


@argIsType(str)
def containsSubstring(substring):
    @argIsType(str)
    def containsSubstring_inner(fullString):
        return fullString.find(substring) != -1

    return containsSubstring_inner
