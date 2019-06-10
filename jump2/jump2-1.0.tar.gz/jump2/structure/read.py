__all__=['convert_value','parse_multiline_string','parse_singletag',
'parse_loop','parse_items','parse_block','parse_cif','format_symbol',
'equival_pos','numbers_cal','lattice_vector','SpacegroupError',
'SpacegroupNotFoundError','SpacegroupValueError']

import os 
from sys import exit
from cif import *
class ReadError(Exception):
    pass
    
class Read(object):
    """
    reading structure
    
    arguments:
        file: path of structure. i.e. /home/xx/xx/POSCAR, POSCAR
        type: type of structure file. i.e. crystal: cif, poscar; molecule: xyz, mol....
    
    """
    
    def __init__(self, file, type=None):
        self.file=file
        
        if type == None:
            if self.file.endswith('.cif'):
                self.type='cif'
            elif self.file.endswith('.xyz'):
                self.type='xyz'
            elif self.file.endswith('.mol'):
                self.type='mol'
            elif self.file.endswith('.vasp'):
                self.type = 'poscar'
            elif any(key in os.path.basename(self.file)
                     for key in ['POSCAR' or 'CONTCAR']):
                self.type='poscar'
            else:
                raise ReadError('please specify the type of file')
        elif type == 'cif':
            self.type='cif'
        elif type.lower() == 'poscar':
            self.type='poscar'
        elif type.lower() == 'xyz':
            self.type='xyz'
        elif type.lower() == 'mol':
            self.type='mol'
        else:
            raise ReadError('unknown type of file!')
        
                    
    def getStructure(self):
        """
        read structure
        
        returns:
            json's object of a structure
            
        """
        if self.type == 'cif':
            return self.__readCIF()
        elif self.type == 'poscar':
            return self.__readPOSCAR()
        elif self.type == 'xyz':
            return self.__readXYZ()
        elif self.type == 'mol':
            return self.__readMOL()
    
    def __readCIF(self):
        """
        read CIF file

        returns:
            cif: A dictionary including:
                 lattice=[[x1,y1,z1],
                         [x2,y2,z2],
                         [x3,y3,z3]]
                 elements=['Ca', 'Fe', 'Sb']
                 numbers=[2, 8, 24]
                 type= Direct
                 positions=[[a1_x,a1_y,a1_z],
                           [a2_x,a2_y,a2_z],
                           [a3_x,a3_y,a3_z],
                           ...]

        """
        import numpy as np
        cf=parse_cif(self.file)
        cb=cf[0][1]

        # lattice parameters
        aa=float(cb['_cell_length_a'])
        bb=float(cb['_cell_length_b'])
        cc=float(cb['_cell_length_c'])
        alpha=float(cb['_cell_angle_alpha'])
        beta=float(cb['_cell_angle_beta'])
        gamma=float(cb['_cell_angle_gamma'])
        alpha=alpha*(math.pi/180)
        beta=beta*(math.pi/180)
        gamma=gamma*(math.pi/180)

        # lattice vector
        lattice=[]
        lattice=lattice_vector(aa, bb, cc, alpha, beta, gamma)

        # elements
        elements=[]
        elements=cb['_atom_site_type_symbol']

        # space group number
        group_number=None
        if '_space_group.it_number' in cb:
            group_number=str(cb['_space_group.it_number'])
        elif '_space_group_it_number' in cb:
            group_number=str(cb['_space_group_it_number'])
        elif '_symmetry_int_tables_number' in cb:
            group_number=str(cb['_symmetry_int_tables_number'])

        # space group H-M symbol
        symbolHM=None
        if '_space_group.Patterson_name_h-m' in cb:
            symbolHM=format_symbol(cb['_space_group.patterson_name_h-m'])
        elif '_symmetry_space_group_name_h-m' in cb:
            symbolHM=format_symbol(cb['_symmetry_space_group_name_h-m'])

        # symmetry operations
        for name in ['_space_group_symop_operation_xyz',
                     '_space_group_symop.operation_xyz',
                     '_symmetry_equiv_pos_as_xyz']:
            if name in cb:
                sitesym=cb[name]
                break
        else:
            sitesym=None

        # positions
        positions=[]
        if sitesym:
            positions=equival_pos(sitesym, cb)
        elif symbolHM:
            if SG.get(symbolHM):
                positions=equival_pos(SG.get(symbolHM), cb)
            else:
                raise SpacegroupNotFoundError('invalid spacegroup %s, not found in data base' %
                                              (symbolHM,))
        elif group_number:
            positions=equival_pos(SG.get(group_number), cb)
        else:
            raise SpacegroupValueError('either *number* or *symbol* must be given for space group!')

        # numbers
        numbers=[]
        if '_atom_site_symmetry_multiplicity' in cb:
            numbers=cb['_atom_site_symmetry_multiplicity']
        elif sitesym:
            numbers=numbers_cal(sitesym, cb)
        elif symbolHM:
            numbers=numbers_cal(SG.get(symbolHM), cb)
        else:
            numbers=numbers_cal(SG.get(group_number), cb)

        # type
        type='Direct'

        lattice=np.array(lattice)
        elements=np.array(elements)
        numbers=np.array(numbers)
        positions=np.array(positions)

        cif={'lattice': lattice,
             'elements': elements,
             'numbers': numbers,
             'type': type,
             'positions': positions}

        return cif       
    
    def __readPOSCAR(self): # only for VASP5.x (It means the file need to contain the element information)
        """
        read POSCAR file
        
        poscar:
            comment: comment of the first line
            lattice=[[x1,y1,z1],
                     [x2,y2,z2],
                     [x3,y3,z3]]
            elements=['Ca', 'Fe', 'Sb']
            numbers=[2, 8, 24]
            type= Direct or Cartesian
            positions=[[a1_x,a1_y,a1_z],
                      [a2_x,a2_y,a2_z],
                      [a3_x,a3_y,a3_z],
                      ...]
            constraints=[[T,T,T], # Selective dynamics (optional)
                        [F,F,F],
                        [T,F,T],
                        ...]
        
        returns:
            json's object of a structure
            
        """
        import numpy as np
        poscar=()
        input=open(self.file)
        
        # comment
        comment=''
        string=input.readline()
        if string != "":
            comment=string.split('\n')[0]
            
        scale=float(input.readline())
        
        # lattice
        # ensure all structure's scale equal 1 inside the program     
        lattice=[]
        for i in xrange(0,3):
            try:
                tmp=np.array([float(s0) for s0 in input.readline().split()])
                if tmp.shape[0] == 3:
                    lattice.append(tmp*scale)
                else:
                    print 'lattice parameter is less than 3!'
                    exit()
            except ValueError:
                print "can't transfer literal to float type!"
                exit()
        lattice=np.array(lattice)
        
        # element VASP5.x
        # Note that:
        #   need check symbol of element is valid by comparing the element table in jump2db
        elements=[]
        tmp=np.array(input.readline().split())
        for i in xrange(0,tmp.shape[0]):
            if not(tmp[i].isalpha()):
                print 'elements contain non-alphabet!'
                exit()
        elements=tmp
        
        # numbers
        numbers=[]
        try:
            tmp=np.array([int(s0) for s0 in input.readline().split()])
            if elements.shape[0] != tmp.shape[0]:
                print "length of numbers don't match with that of elements"
                exit()
            numbers=tmp
        except ValueError:
            print "can't transfer literal to int type!"
            exit()
            
        
        tmp=input.readline()
        isConstraint=False
        type=''
        if tmp.lower().startswith('s'): # Selective dynamics
            isConstraint=True
            # type
            tmp=input.readline()
            if tmp.lower().startswith('c'):
                type='Cartesian'
            elif tmp.lower().startswith('d'):
                type='Direct'
            else:
                print 'type of POSCAR is invalid'
                exit()
        # type    
        elif tmp.lower().startswith('c'):
            type='Cartesian'
        elif tmp.lower().startswith('d'):
            type='Direct'
        else:
            print 'type of POSCAR is invalid'
            exit()
        
        # position
        natoms=sum(numbers)
        positions=[]
        constraints=[]
        for i in xrange(0, natoms):
            try:
                string=input.readline().split()
                if (not isConstraint and len(string) <3) or (isConstraint and len(string) != 6):
                    print 'column of position not enough!'
                    exit()
                tmp=np.array([float(s0) for s0 in string[:3]])
                positions.append(tmp)
                
                # constraint
                if isConstraint:
                    tmp=np.array([False if s0.startswith('F') else True for s0 in string[3:6]])
                    constraints.append(tmp)
                    
            except ValueError:
                print "can't transfer literal to float type!"
                exit()
        positions=np.array(positions)
        constraints=np.array((constraints))
        
        input.close()
        #poscar=(comment,lattice,elements,numbers,type,positions,constraints)
        poscar={'comment':comment,
                'lattice':lattice,
                'elements':elements,
                'numbers':numbers,
                'type':type,
                'positions':positions,
                'constraints':constraints}
        return poscar

    def __readXYZ(self):
        """
        read xyz file
            
        poscar:
            elements=['Ca', 'Fe', 'Sb']
            numbers=[2, 8, 24]
            positions=[[a1_x,a1_y,a1_z],
                      [a2_x,a2_y,a2_z],
                      [a3_x,a3_y,a3_z],
                      ...]
        Note: coordinate type of positions can only be Cartesian.
        
        returns:
            object of a structure
        """
        import numpy as np
        xyz=()
        input=open(self.file)
        
        # natoms
        try:
            natoms=int(input.readline())
        except ValueError:
            return ValueError('invalid natoms in xyz file!')
        
        # comment
        comment=input.readline() # skip
        
        # atoms
        counter=0 # counter of atoms
        atoms={}
        string=input.readline()
        while(string):
            if string.split() != []: # skip blank line
                ntmp=string.split()[0] # atomic name
                try:
                    ptmp=np.array([float(s0) for s0 in string.split()[1:]]) # atomic position
                except ValueError:
                    raise ValueError('invalid atomic position in xyz file!')
                
                if ntmp in atoms.keys():
                    value=atoms[ntmp]
                    atoms[ntmp]=np.vstack((value,ptmp))
                else:
                    atoms[ntmp]=ptmp
                counter=counter+1
                string=input.readline()
                
        if counter != natoms:
            raise ReadError("number of atoms doesn't match!")
        
        # conversion format
        molecule={}
        molecule['elements']=np.array(atoms.keys())
        numbers=[]
        positions=[]
        for e in atoms.keys():
            dim=atoms[e].shape
            if len(dim) == 1 and dim[0] == 3:
                numbers.append(1)
                positions.append(atoms[e])
            elif len(dim) == 2 and dim[1] == 3:
                numbers.append(dim[0])
                for p in xrange(0,dim[0]):
                    positions.append(atoms[e][p])
            else:
                raise ReadError('invalid atomic position!')
            
        molecule['numbers']=np.array(numbers)
        molecule['positions']=np.array(positions)
        
        return molecule
                
    def __readMOL(self):
        """
        """
        pass

    # write structure % 
   ##def write_structure(self, format='vasp', direct=True, isvasp5=True):
   #def write(self, stdout, format='vasp', direct=True, **kwargs):
   #   
   #   if format is 'vasp':
   #       from ..utils.io import vasp_write
   #       vasp_write(self.structure, direct=True, **kwargs)

from structure import Structure 
import numpy as np 
def reader(self, name='POSCAR', type=type):
    
    obj = Structure()
    structure   = Read('CONTCAR', type=type).getStructure()
    
    obj.comment = structure['comment']
    obj.lattice = np.array(structure['lattice'])
    if structure['type'].lower() == 'direct': 
        obj.direct = True 
    if len(structure['constraints']) == 0:
        obj.frozen = False 
    else:
        obj.frozen = True 
        obj.fz_xyz = structure['constraints']
    obj.elements = structure['elements'] 
    obj.num_elements = structure['numbers']
    obj.positions = np.array(structure['positions'])
   
    return obj  
