'''
Created on Oct 21, 2017

@author: Xin He, Yuhao Fu
'''
from __future__ import unicode_literals

from jump2.db.materials.element import Element
from jump2.db.materials.molElement import MolElement

"""
element{symbol:[z, name, period, group, mass, atomic radius, electronegativity],
       ...
       }
"""

elements={'H'  :[  1,'Hydrogan',   1, 1,  1.007825,   25,2.2],
        'He' :[  2,'Helium',       1,18,  4.002602,   31,'*'],
        'Li' :[  3,'Lithium',      2, 1,  6.938,     145,0.98],
        'Be' :[  4,'Beryllium',    2, 2,  9.012182,  105,1.57],
        'B'  :[  5,'Boron',        2,13, 10.806,      85,2.04],
        'C'  :[  6,'Carbon',       2,14, 12.0096,     70,2.55],
        'N'  :[  7,'Nitrogen',     2,15, 14.00643,    65,3.04],
        'O'  :[  8,'Oxygen',       2,16, 15.99903,    60,3.44],
        'F'  :[  9,'Fluorine',     2,17, 18.9984032,  50,3.98],
        'Ne' :[ 10,'Neon',         2,18, 20.1797,     38,'*'],
        'Na' :[ 11,'Sodium',       3, 1, 22.98976928,180,0.93],
        'Mg' :[ 12,'Magnesium',    3, 2, 24.304,     150,1.31],
        'Al' :[ 13,'Aluminium',    3,13, 26.9815386, 125,1.61],
        'Si' :[ 14,'Silicon',      3,14, 28.084,     110,1.9],
        'P'  :[ 15,'Phosphorus',   3,15, 30.973762,  100,2.19],
        'S'  :[ 16,'Sulfer',       3,16, 32.059,     100,2.58],
        'Cl' :[ 17,'Chlorion',     3,17, 35.446,     100,3.16],
        'Ar' :[ 18,'Argon',        3,18, 39.948,      71,'*'],
        'K'  :[ 19,'Potassium',    4, 1, 39.0983,    220,0.82],
        'Ca' :[ 20,'Calcium',      4, 2, 40.078,     180,1],
        'Sc' :[ 21,'Scandium',     4, 3, 44.955912,  160,1.36],
        'Ti' :[ 22,'Titanium',     4, 4, 47.867,     140,1.54],
        'V'  :[ 23,'Vanadium',     4, 5, 50.9415,    135,1.63],
        'Cr' :[ 24,'Chromium',     4, 6, 51.9961,    140,1.66],
        'Mn' :[ 25,'Manganese',    4, 7, 54.938045,  140,1.55],
        'Fe' :[ 26,'Iron',         4, 8, 55.845,     140,1.83],
        'Co' :[ 27,'Cobalt',       4, 9, 58.933195,  135,1.88],
        'Ni' :[ 28,'Nickel',       4,10, 58.6934,    135,1.91],
        'Cu' :[ 29,'Copper',       4,11, 63.546,     135,1.90],
        'Zn' :[ 30,'Zinc',         4,12, 65.38,      135,1.65],
        'Ga' :[ 31,'Gallium',      4,13, 69.723,     130,1.81],
        'Ge' :[ 32,'Germanium',    4,14, 72.63,      125,2.01],
        'As' :[ 33,'Arsenic',      4,15, 74.9216,    115,2.18],
        'Se' :[ 34,'Selenium',     4,16, 78.96,      103,2.55],
        'Br' :[ 35,'Bromine',      4,17, 79.901,      94,2.96],
        'Kr' :[ 36,'Krypton',      4,18, 83.798,      88,3],
        'Rb' :[ 37,'Rubidium',     5, 1, 85.4678,    235,0.82],
        'Sr' :[ 38,'Strontium',    5, 2, 87.62,      200,0.95],
        'Y'  :[ 39,'Yttrium',      5, 3, 88.90585,   180,1.22],
        'Zr' :[ 40,'Zirconium',    5, 4, 91.224,     155,1.33],
        'Nb' :[ 41,'Niobium',      5, 5, 92.90638,   145,1.6],
        'Mo' :[ 42,'Molybdenum',   5, 6, 95.96,      145,2.16],
        'Tc' :[ 43,'Technetium',   5, 7,'*',         135,1.9],
        'Ru' :[ 44,'Ruthenium',    5, 8,101.07,      130,2.2],
        'Rh' :[ 45,'Rhodium',      5, 9,102.9055,    135,2.28],
        'Pd' :[ 46,'Palladium',    5,10,106.42,      140,2.2],
        'Ag' :[ 47,'Silver',       5,11,107.8682,    160,1.93],
        'Cd' :[ 48,'Cadmium',      5,12,112.41,      155,1.69],
        'In' :[ 49,'Indium',       5,13,114.818,     155,1.78],
        'Sn' :[ 50,'Tin',          5,14,118.71,      145,1.96],
        'Sb' :[ 51,'Antimony',     5,15,121.76,      145,2.05],
        'Te' :[ 52,'Tellurium',    5,16,127.6,       140,2.1],
        'I'  :[ 53,'Iodine',       5,17,126.90447,   140,2.66],
        'Xe' :[ 54,'Xenon',        5,18,131.293,     108,2.6],
        'Cs' :[ 55,'Cesium',       6, 1,132.9054519, 260,0.79],
        'Ba' :[ 56,'Barium',       6, 2,137.327,     215,0.89],
        'La' :[ 57,'Lanthanum',    6, 2,138.90547,   195,1.1],
        'Ce' :[ 58,'Cerium',       6, 2,140.116,     185,1.12],
        'Pr' :[ 59,'Praseodymium', 6, 2,140.90765,   185,1.13],
        'Nd' :[ 60,'Neodymium',    6, 2,144.242,     185,1.14],
        'Pm' :[ 61,'Promethium',   6, 2,'*',         185,'*'],
        'Sm' :[ 62,'Samarium',     6, 2,150.36,      185,1.17],
        'Eu' :[ 63,'Europium',     6, 2,151.964,     185,1.2],
        'Gd' :[ 64,'Gadolinium',   6, 2,157.25,      180,1.2],
        'Tb' :[ 65,'Terbium',      6, 2,158.92535,   175,'*'],
        'Dy' :[ 66,'Dysprosium',   6, 2,162.5,       175,1.22],
        'Ho' :[ 67,'Holmium',      6, 2,164.93032,   175,1.23],
        'Er' :[ 68,'Erbium',       6, 2,167.259,     175,1.24],
        'Tm' :[ 69,'Thulium',      6, 2,168.93421,   175,1.25],
        'Yb' :[ 70,'Ytterbium',    6, 2,173.054,     175,'*'],
        'Lu' :[ 71,'Lutetium',     6, 3,174.9668,    175,1.27],
        'Hf' :[ 72,'Hafnium',      6, 4,178.49,      155,1.3],
        'Ta' :[ 73,'Tantalum',     6, 5,180.94788,   145,1.5],
        'W'  :[ 74,'Wolfram',      6, 6,183.84,      135,2.36],
        'Re' :[ 75,'Rhenium',      6, 7,186.207,     135,1.9],
        'Os' :[ 76,'Osmium',       6, 8,190.23,      130,2.2],
        'Ir' :[ 77,'Iridium',      6, 9,192.217,     135,2.2],
        'Pt' :[ 78,'Platinum',     6,10,195.084,     135,2.28],
        'Au' :[ 79,'Gold',         6,11,196.966569,  135,2.54],
        'Hg' :[ 80,'Mercury',      6,12,200.592,     150,2],
        'Tl' :[ 81,'Thallium',     6,13,204.382,     190,1.62],
        'Pb' :[ 82,'Lead',         6,14,207.2,       180,2.33],
        'Bi' :[ 83,'Bismuth',      6,15,208.9804,    160,2.02],
        'Po' :[ 84,'Polonium',     6,16,'*',         190,2],
        'At' :[ 85,'Astatine',     6,17,'*',         '*',2.2],
        'Rn' :[ 86,'Radon',        6,18,'*',         120,2.2],
        'Fr' :[ 87,'Francium',     7, 1,'*',         '*',0.7],
        'Ra' :[ 88,'Radium',       7, 2,'*',         215,0.9],
        'Ac' :[ 89,'Actinium',     7, 2,'*',         195,1.1],
        'Th' :[ 90,'Thorium',      7, 2,232.03806,   180,1.3],
        'Pa' :[ 91,'Protactinium', 7, 2,231.03588,   180,1.5],
        'U'  :[ 92,'Uranium',      7, 2,238.02891,   175,1.38],
        'Np' :[ 93,'Neptunium',    7, 2,'*',         175,1.36],
        'Pu' :[ 94,'Plutonium',    7, 2,'*',         175,1.28],
        'Am' :[ 95,'Americium',    7, 2,'*',         175,1.3],
        'Cm' :[ 96,'Curium',       7, 2,'*',         '*',1.3],
        'Bk' :[ 97,'Berkelium',    7, 2,'*',         '*',1.3],
        'Cf' :[ 98,'Californium',  7, 2,'*',         '*',1.3],
        'Es' :[ 99,'Einsteinium',  7, 2,'*',         '*',1.3],
        'Fm' :[100,'Fermium',      7, 2,'*',         '*',1.3],
        'Md' :[101,'Mendelevium',  7, 2,'*',         '*',1.3],
        'No' :[102,'Nobelium',     7, 2,'*',         '*',1.3],
        'Lr' :[103,'Lawrencium',   7, 3,'*',         '*','*'],
        'Rf' :[104,'Rutherfordium',7, 4,'*',         '*','*'],
        'Db' :[105,'Dubnium',      7, 5,'*',         '*','*'],
        'Sg' :[106,'Seaborgium',   7, 6,'*',         '*','*'],
        'Bh' :[107,'Bohrium',      7, 7,'*',         '*','*'],
        'Hs' :[108,'Hassium',      7, 8,'*',         '*','*'],
        'Mt' :[109,'Mietnerium',   7, 9,'*',         '*','*'],
        'Ds' :[110,'Darmstadium',  7,10,'*',         '*','*'],
        'Rg' :[111,'Roentgenium',  7,11,'*',         '*','*'],
        'Cn' :[112,'Copernicium',  7,12,'*',         '*','*'],
        'Unt':[113,'Ununtrium',    7,13,'*',         '*','*'],
        'Fl' :[114,'Flerovium',    7,14,'*',         '*','*'],
        'Unp':[115,'Ununpentium',  7,15,'*',         '*','*'],
        'Lv' :[116,'livermorium',  7,16,'*',         '*','*'],
        'Uus':[117,'Ununseptium',  7,17,'*',         '*','*'],
        'Uno':[118,'Ununoctium',   7,18,'*',         '*','*']
        }

class InitializeElementError(Exception):
    pass


class InitializeElement():
    """
    initialize the element table for crystal in jump2db
    
    Examples:
        For one element:
        >>> InitializeElement('H')
        
        For all elements:
        >>> InitializeElement()
    """
    def __init__(self, symbol=None):
        """
        Arguments:
            symbol: element symbol. i.e. 'H'
        """
        if symbol == None:
            self.initializeElementAll()
        else:
            self.initializeElement(symbol)

    def initializeElementAll(self):
        """
        initialize periodic table
        """
        # element
        for (key, value) in elements.items():
            #print '>>', key, ' <> ', value
            symbol=key
            z=value[0]
            name=value[1]
            period=value[2]
            group=value[3]
            mass=value[4]
            electronegativity=value[6]
        
            element, iscreate=Element.objects.get_or_create(z=z,name=name,symbol=symbol,group=group,period=period)
            #element=Element(z=z,name=name,symbol=symbol,group=group,period=period)
        
            if mass != '*':
                element.mass=mass     
                                    
            if electronegativity != '*':
                element.electronegativity=electronegativity
            element.save()
            
    def initializeElement(self, symbol):
        """
        initialize a specified element
        """
        value=elements.get(symbol)
        if value == None:
            raise InitializeElementError('unknown element!')
    
        z=value[0]
        name=value[1]
        period=value[2]
        group=value[3]
        mass=value[4]
        electronegativity=value[6]
        
        element, iscreate=Element.objects.get_or_create(z=z,name=name,symbol=symbol,group=group,period=period)
        #element=Element(z=z,name=name,symbol=symbol,group=group,period=period)
        
        if mass != '*':
            element.mass=mass    
                                    
        if electronegativity != '*':
            element.electronegativity=electronegativity
        element.save()   
 
# molecule            
class InitializeMolElementError(Exception):
    pass


class InitializeMolElement():
    """
    initialize the element table for molecule in jump2db
    
    Examples:
        For one element:
        >>> InitializeElement('H')
        
        For all elements:
        >>> InitializeElement()
    """
    
    def __init__(self, symbol=None):
        """
        Arguments:
            symbol: element symbol
        """
        if symbol == None:
            self.initializeMolElementAll()
        else:
            self.initializeMolElement(symbol)

    def initializeMolElementAll(self):
        """
        initialize periodic table
        """
        # element
        for (key, value) in elements.items():
            #print '>>', key, ' <> ', value
            symbol=key
            z=value[0]
            name=value[1]
            period=value[2]
            group=value[3]
            mass=value[4]
            electronegativity=value[6]
        
            element, iscreate=MolElement.objects.get_or_create(z=z,name=name,symbol=symbol,group=group,period=period)
            #element=MolElement(z=z,name=name,symbol=symbol,group=group,period=period)
            
            if mass != '*':
                element.mass=mass    
                                    
            if electronegativity != '*':
                element.electronegativity=electronegativity
            element.save()
            
    def initializeMolElement(self, symbol):
        """
        initialize a specified element
        """
        value=elements.get(symbol)
        if value == None:
            raise InitializeMolElementError('unknown element!')
    
        z=value[0]
        name=value[1]
        period=value[2]
        group=value[3]
        mass=value[4]
        electronegativity=value[6]
        
        element, iscreate=MolElement.objects.get_or_create(z=z,name=name,symbol=symbol,group=group,period=period)
        #element=MolElement(z=z,name=name,symbol=symbol,group=group,period=period)
        
        if mass != '*':
            element.mass=mass     
                                    
        if electronegativity != '*':
            element.electronegativity=electronegativity
        element.save()
            
