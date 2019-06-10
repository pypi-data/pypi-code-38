

__contributor__ = 'xingang zhao, xingang.zhao@colorado.edu'

class SelectDynamic(object):
    
    def __init__(self,f=None):
 
	if f is not None: 
            self.x = f[0]
            self.y = f[1]
            self.z = f[2]
        self.__f = f 
 
    @property
    def xyz(self):
        return self.__f 
   
    def __repr__(self):
	s= "%s" % ([self.x, self.y, self.z])
        return s  

import numpy as np

class Cell(object):

    """
    cls Lattice aim to define the lattice vector. 
   
    properties:
        length a, b, c; 
        angle alpha, beta, gamma; 
        cell volume; 
        scale: scale lattice vectors;
        vectors: 3x3 numpy.array; 
   function:
        get_cell: return self.vectors, i.e., 3x3 vectors;	 
    """

    def __init__(self, cell=None, scale=1.0):
        
	self.__scale = scale 
        if cell is not None:
            self.__cell = np.array(cell)*self.__scale 
   
    @property
    def a(self):
        if self.__cell is not None: 
            return np.linalg.norm(self.__cell[0])
        else: 
            return None 

    @property
    def b(self):
        if self.__cell is not None: 
            return np.linalg.norm(self.__cell[1])
        else: 
            return None 
    @property
    def c(self):
        if self.__cell is not None: 
            return np.linalg.norm(self.__cell[2])
        else: 
            return None 
    @property
    def alpha(self):
        if self.__cell is not None: 
            value=np.dot(self.__cell[0],self.__cell[1])/(self.a*self.b)
            return np.acos(value)/np.pi*180
        else: 
            return None 
    @property
    def beta(self):
        if self.__cell is not None: 
            value=np.dot(self.__cell[1],self.__cell[2])/(self.b*self.c)
            return np.acos(value)/np.pi*180
        else: 
            return None 
    @property
    def gamma(self):
        if self.__cell is not None: 
            value=np.dot(self.__cell[0],self.__cell[2])/(self.a*self.c)
            return np.acos(value)/np.pi*180
        else: 
            return None
    
    @property
    def volume(self):
        if self.__cell is not None: 
            return np.dot(\
		   np.cross(self.__cell[0],self.__cell[1]),self.__cell[2])
        else: 
            return None 

    @property     
    def vectors(self):
        return np.matrix(self.__cell, float)
	
    @property 
    def scale(self):
	return self.__scale

    @scale.setter
    def scale(self, value=1.0):
        if isinstance(value, float) or isinstance(value, int):
           self.__scale = float(value)
	   self.__cell  = self.__cell*value

    @property
    def reciprocal(self):
        return self.vectors.I 

    def __repr__(self):
        s=''
        if self.__cell is not None:
            s = "lattice info:\n"
            s += " length    a (A) : %f\n" % (self.a)  
            s += " length    b (A) : %f\n" % (self.b)  
            s += " length    c (A) : %f\n" % (self.c)  
            s += " cell volume(A^3): %f\n" % (self.volume)  
            s += " lattice vectors:\n" 
            #s += ' '.join("%s\n" % (list(self.vectors[0])))
            s += ' '.join("%s\n" % (list(v)) for v in self.vectors[0])
            s += ' '.join("%s\n" % (list(v)) for v in self.vectors[1])
            s += ' '.join("%s\n" % (list(v)) for v in self.vectors[2])
            #s += "%s\n" % (list(self.vectors[1]))
            #s += "%s\n" % (list(self.vectors[2]))

	return s 

class Position(object):
    def __init__(self, coord):
        self.x = coord[0]
        self.y = coord[1]
        self.z = coord[2]
        self.xyz = coord 

    def __repr__(self):
        return "%s" % ([self.x, self.y, self.z])
    
class Coord(object):


    def __init__(self, coord):
        self.__position = coord

    @property 
    def direct(self):
        return Position(self.__position[0])
    @direct.setter
    def direct(self, value=None):
        if value is not None:
            self.__position[0]=np.array(value) 
    @property
    def cartesian(self):
        return Position(self.__position[1])
    
    @cartesian.setter
    def cartesian(self, value=None):
        if value is not None:
            self.__position[1]=np.array(value) 
    
    def __repr__(self):
        s= "Direct:["
        for v in self.__position[0]:
            s += "{0:>12.8f}".format(v)
        s += "]" 
        return s  
    
class AtomOccupation(object):
    """
    cls to define one position, including,
          index
          element
          occupied coordination 
          charge 
          magnetic
          constraint
    """   
    def __init__(self, index, element, position, \
                  magnetic=None, charge=None, freeze=None, \
		  *args, **kwargs):
	
        # freeze the atom or not %
        self.__freeze = None 
        self.__specie = element
        self.__index  = index
        self.__charge = charge 
        self.__magnetic = magnetic 
        self.__charge = charge 
        self.__occup = Coord(position)

    # index % 	 
    @property
    def index(self):
        return self.__index
 
    # for elemenets % 
    @property
    def specie(self):
	return self.__specie 
    @specie.setter
    def specie(self, value=None):
        if value is not None and isinstance(value,str):
            self.__specie = value 

    # occupied coordination %         
    @property
    def occupation(self):
        """
        return an object of position 
        """
        return  self.__occup

    @occupation.setter
    def occupation(self, value=None):
        """
        Note only accept cartesian coordition 
        """
        occ=[None,None]
        occ[0]=np.array(self.occupation.direct.xyz)
        if isinstance(value, list):
            occ[1]=np.array(value)
        if isinstance(value, Coord):
            occ[1]=value.cartesian.xyz
        if isinstance(value, Position):
            occ[1]=value.xyz
        self.__occup = Coord(occ)

    # magnetic % 
    @property 
    def magnetic(self):
        return self.__magnetic
    @magnetic.setter
    def magnetic(self, value=None):
        if value is not None:
            self.__magnetic = value  
    
    # charge %   
    @property 
    def charge(self):
        return self.__charge 
    
    @charge.setter
    def charge(self,value=None):
        if value is not None:
            self.__charge = charge 
      
    # freeze x/y/z % 
    @property  
    def freeze(self):
	return SelectDynamic(self.__freeze) 
    
    @freeze.setter 
    def freeze(self, value=None):
        if isinstance(value, bool):
           self.__freeze = [value]*3
	elif isinstance(value,SelectDynamic):
	    self.__freeze = [value.x, value.y, value.z]
        elif isinstance(value,list):
	    self.__freeze = value 
        else:
            raise IOError ("No size (1,3) list")
    
    def __repr__(self):
        s = ''
        s += "(No. %s, Element: %s, Position: %s" \
               % (self.index, self.specie, self.occupation)
        if self.__freeze is not None: s += ", Freeze: %s" % (self.freeze) 
        if self.__charge is not None: s += ", Charge: %s" % (self.charge)
        if self.__magnetic is not None: s += ", Magnetic: %s" % (self.magnetic)
        s += ")"   
        return s 
        
