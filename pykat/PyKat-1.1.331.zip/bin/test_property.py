import abc
import pykat.exceptions as pkex

class puttable(object):
    """
    Objects that inherit this should be able to have something `put` to it.
    Essentially this means you could write Finesse commands like
    
    put this parameter value
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, component_name, parameter_name):
        self._parameter_name = parameter_name
        self._component_name = component_name
        self._putter = None
    
    def put(self, var):
        if not isinstance(var, putter):
            raise pkex.BasePyKatException("var was not something that can be `put` as a value")
        
        if self._putter != None:
            self._putter.put_count -= 1
        
        self._putter = var
        self._putter.put_count += 1
        
    def getPutFinesseText(self):
        rtn = []
        # if something is being put to this 
        if self._putter != None:
            rtn.append("put {comp} {param} ${value}".format(comp=self._component_name, param=self._parameter_name, value=self._putter.put_name()))
        
        return rtn
            
class putter(object):
    """
    If an object can be put to something that is puttable it should inherit this
    object.
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, put_name):
        self._put_name = put_name
        self.put_count = 0
        
    def put_name(self): return self._put_name
    
        
class Param(puttable, putter):         
    def __init__(self, name, owner, value):
        self._name = name
        self._owner = owner
        self._value = value
        
        putter.__init__(self,"var_{0}_{1}".format(owner.name, name))
        puttable.__init__(self, owner.name, name)
        
    @property
    def name(self): return self._name
    
    @property
    def value(self): return self._value
    @value.setter
    def value(self, value):
        self._value = value
    
    def __float__(self): return self.value
        
    def getFinesseText(self):
        rtn = []
        rtn.extend(self.getPutFinesseText())
        
        # if this parameter is being put somewhere then we need to
        # set it as a variable
        if self.put_count > 0:
            rtn.append("set {put_name} {comp} {param}".format(put_name=self.put_name(), comp=self._owner.name, param=self.name))
        
        return rtn
        
    def __mul__(self, a):
        return float(self) * a
    
    def __imul__(self, a):
        return self.value * float(a)
        
    __rmul__ = __mul__
    
    def __add__(self, a):
        return self.value + flota(a)
    
    def __iadd__(self, a):
        return self.value + float(a)
        
    __radd__ = __add__
    
    def __sub__(self, a):
        return self.value - float(a)
    
    def __isub__(self, a):
        return self.value - float(a)
        
    __rsub__ = __sub__
    
    def __div__(self, a):
        return self.value / float(a)
    
    def __idiv__(self, a):
        return self.value / complex(a)
        
    def __pow__(self, q):
        return  self.value**q

    def __neg__(self):
        return -self.value
        
    def __eq__(self, q):
        return float(q) == self.value
        
class Beer(object):
    def __init__(self, temp, name):
        
        self._name = name
        
        self._T = Param('T', self, temp)
    
    @property
    def name(self): return self._name
        
    @property
    def T(self): return self._T
    
    @T.setter
    def T(self,value): self._T.value = float(value) 
        

b = Beer(1,"b")
c = Beer(2,"c")

c.T.put(b.T)

print c.T.getFinesseText()
print b.T.getFinesseText()