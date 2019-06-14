

class Vector:
    def __init__(self, start, *, end = None, size = None):
        assert (end is None) != (size is None), f'Should specify "end" XOR "size"'
        
        self.s = start
        self.e = (start + size - 1) if end is None else end
        self.nb = self.e - self.s + 1
        
    def Intersects(self, v: 'Vector') -> bool:
        if v.s > self.e or self.s > v.e:
            return False
        return True

    def IsEqual(self, v: 'Vector') -> bool:
        return self.s == v.s and self.e == v.e

    def Contains(self, v: 'Vector') -> bool:
        return self.s <= v.s and self.e >= v.e

    def GetIntersection(self, v: 'Vector') -> 'Vector':
        s = max ((self.s, v.s))
        e = min ((self.e, v.e))
        
        return Vector(s, end=e)

    def __str__(self) -> str:
        return 'Vector[{} .. {} (size={})]'.format(self.s, self.e, self.nb)
