# coding: utf-8
# Copyright (c) JUMP2 Development Team.
# Distributed under the terms of the JLU License.


#=================================================================
# This file is part of JUMP2.
#
# Copyright (C) 2017 Jilin University
#
#  Jump2 is a platform for high throughput calculation. It aims to 
#  make simple to organize and run large numbers of tasks on the 
#  superclusters and post-process the calculated results.
#  
#  Jump2 is a useful packages integrated the interfaces for ab initio 
#  programs, such as, VASP, Guassian, QE, Abinit and 
#  comprehensive workflows for automatically calculating by using 
#  simple parameters. Lots of methods to organize the structures 
#  for high throughput calculation are provided, such as alloy,
#  heterostructures, etc.The large number of data are appended in
#  the MySQL databases for further analysis by using machine 
#  learning.
#
#  Jump2 is free software. You can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published 
#  by the Free sofware Foundation, either version 3 of the License,
#  or (at your option) and later version.
# 
#  You should have recieved a copy of the GNU General Pulbic Lincense
#  along with Jump2. If not, see <https://www.gnu.org/licenses/>.
#=================================================================

"""
Module for extract data from vasp output: data for band structure. 
"""

__contributors__ = 'Xin-Gang Zhao'
__maintainer__ = 'Xin-Gang Zhao'

from basic import TotalEnergy
import numpy as np 


class BasicParam(TotalEnergy):

    """
    class get the baisc parameters from the VASP output.
    """

    def __init__(self, path=None):

        super(BasicParam).__init__()
        
        self.__isif = None 
        self.__version = None
         
    @property
    def isif(self):
	self.__isif 

    @isif.setter
    def isif(self, path=None):
        
	import commands 

        indir = os.path.join(path, 'OUTCAR')
        command = 'grep ISIF {inp}'
        content = commands.getoutput(command.format(inp=indir))
       	content = re.findall(r"=(?=)+\s*(\d)",content)[0]
        isif    = int(content)
        
        self.__isif = isif 
    @property
    def vasp_version(self):

        return self.__version
    
    @vasp_version.setter
    def vsap_version(self, path=None):
        
	import commands 

        indir = os.path.join(path, 'OUTCAR')
        command = 'head -1 {inp}'
        content = commands.getoutput(command.format(inp=indir))
       	content = re.findall(r"vasp.(?=)(\S*)",content)[0]
        version = np.int64(content.split('.')[0:2])
        
        self.__version = str('{0}.{1}'.format(version))

class ExtractOutcar(object):

    def __init__(self):
        self._path = os.getcwd()

    def search_factory(name, methname, filename=None):
        if filename is None: filename = methname.upper()
        doc = \
            """ A mixin to include standard methods to search {0}.

                This mixin only includes the search methods themselves. The derived
                class should define the appropriate {1} attribute.
            """.format(filename, methname.upper())

        def rsearch_OUTCAR(self, regex, flags=0):
            from re import compile, M as moultline

            regex = compile(regex)
            with open('OUTCAR', 'r') as file:
                if moultline & flags:
                    lines = file.read()
                else:
                    lines = file.readline()

            if moultline & flags:
                for v in [u for u in regex.finditer(lines)][::-1]: yield v
            else:
                for line in lines[::-1]:
                    found = regex.search(line)
                    if found is not None: yield found

        rsearch_OUTCAR.__name__ = 'rsearch_{0}'.format(methname.upper())

        def _find_last_OUTCAR(self, regex, flags=0):
            for last in getattr(self, rsearch_OUTCAR.__name__)(regex, flags): return last
            return None

        _find_last_OUTCAR.__name__ = '_find_last_{0}'.format(methname.upper())

        def ialgo(self):
            # Find line like:  IALGO  =     68    algorithm
            result = self._find_last_OUTCAR(r"""^\s*IALGO\s*=\s*(\d+)\s*""")
            return int(result.group(1))

        def algo(self):
            return {68: 'Fast', 38: 'Normal', 48: 'Very Fast', 58: 'Conjugate',
                    53: 'Damped', 4: 'Subrot', 90: 'Exact', 2: 'Nothing'}[self.ialgo]

        def precision(self):
            result = self._find_last_OUTCAR(r"""\s*PREC\s*=\s*(\S*)\s+""")
            if result is None: return None
            if result.group(1) == "accura": return "accurate"
            return result.group(1)

        def istart(self):
            result = self._find_last_OUTCAR((r"""\s*ISTART\s*=\s*(\d+)\s+"""))
            if result is not None:
                return int(result.group(1))

        def icharg(self):
            result = self._find_last_OUTCAR(r"""\s*ICHARG\s*=\s*(\d+)\s+""")
            if result is not None:
                return int(result.group(1))

        def lnoncollinear(self):
            result = self._find_last_OUTCAR(r"""\s*LNONCOLLINEAR\s*=\s*(\S+)\s+""")
            return result.group(1)

        def nelmdl(self):
            regex = (r"""^s*NELM\s*=\s*\d+\s*;"""\
                      """^s*NELMIN\s*=\s*\d+\s*;""" \
                     """^s*NELMDL\s*=\s*\d+\s*;""" )
            result = self._find_last_OUTCAR(regex)
            if result is not None:
                return int(result.group(1))

        def lreal(self):
            result = self._find_last_OUTCAR(r"""\s*LREAL\s*=\s*(\S+)\s+""")
            if result is not None:
                return result.group(1)

        def isym(self):
            result = self._find_last_OUTCAR(r"""\s*ISYM\s*=\s*(\d+)\s+""")
            if result is not None:
                return int(result.group(1))

        def weimin(self):
            result = self._find_last_OUTCAR(r"""\s*WEIMIN\s*=\s(\d+.\d+)\s+""")
            if result is not None:
                return float(result.group(1))

        def lexch(self):
            result = self._find_last_OUTCAR(r"""\s*LEXCH\s*=\s*(\d+)\s+""")
            if result is not None:
                return int(result.group(1))

        def voskown(self):
            result = self._find_last_OUTCAR(r"""\s*VOSKOWN\s*=\s*(\d+)\s+""")
            if result is not None:
                return int(result.group(1))

        def lhfcalc(self):
            result = self._find_last_OUTCAR(r"""\s*LHFCALC\s*=\s*(\S+)\s+""")
            if result is not None:
                return result.group(1)

        def lhfone(self):
            result = self._find_last_OUTCAR(r"""\s*LHFONE\s*=\s*(\S+)\s+""")
            if result is not None:
                return result.group(1)

        def aexx(self):
            result = self._find_last_OUTCAR(r"""\s*AEXX\s*=\s*(\d+)\s+""")
            if result is not None:
                return float(result.group(1))

        def encut(self):
            from quantities import eV
            return float(self._find_last_OUTCAR(r"ENCUT\s*=\s*(\S+)").group(1)) * eV

        def success(self):
            """
            Check that VASP run has completed
            """
            regex = compile(r"""General\s+timing\s+and\s+accounting\s+informations\s+for\s+this\s+job""")
            found = self._find_last_OUTCAR(regex)
            if found is None:
                raise CalError("This calculation is not conpleted, pleasw check the file")
            else:
                return True

        def isif(self):
            result = self._find_last_OUTCAR(r"""\s*ISIF\s*=\s*(-?\d+)\s+""")
            if result is not None:
                return int(result.group(1))

        def nsw(self):
            result = self._find_last_OUTCAR(r"""\s*NSW\s*=\s*(-?\d+)\s+""")
            if result is not None:
                return int(result.group(1))

        def ismear(self):
            result = self._find_last_OUTCAR(r"""\s*ISMEAR\s*=\s*(\d+);""")
            if result is not None:
                return int(result.group(1))

        def sigma(self):
            from numpy import array
            from quantities import eV

            result = self._find_last_OUTCAR(r"""\s*ISMEAR\s*=\s*(?:\d+)\s*;\s*SIGMA\s*=\s+(.*)\s+br""")
            if result is None: return None
            result = result.group(1).rstrip().lstrip().split()
            if len(result) == 1: return float(result[0]) * eV
            return array(result, dtype="float64") * eV

        def ibrion(self):
            result = self._find_last_OUTCAR(r"""\s*IBRION\s*=\s*(-?\d+)\s+""")
            if result is not None:
                return int(result.group(1))

        def potim(self):
            result = self._find_last_OUTCAR(r"""\s*POTIM\s*=\s*(-?\S+)\s+""")
            if result is not None:
                return float(result.group(1))

        def lorbit(self):
            result = self._find_last_OUTCAR(r"""\s*LORBIT\s*=\s*(\d+)\s+""")
            if result is not None:
                return int(result.group(1))

        def isym(self):
            result = self._find_last_OUTCAR(r"""\s*ISYM\s*=\s*(\d+)\s+""")
            if result is not None:
                return int(result.group(1))

        def lmaxmin(self):
            result = self._find_first_OUTCAR(r"""\s*LMAXMIX\s*=\s*(\d+)\s+""")
            if result is not None:
                return int(result.group(1))

        def ediff(self):
            result = self._find_last_OUTCAR(r"""\s*EDIFF\s*=\s*(\S+)\s+*""")
            if result is not None:
                return float(result.group(1))

        def ediffg(self):
            result = self._find_last_OUTCAR(r"""\s*EDIFF\s*=\s*(\S+)\s+*""")
            if result is not None:
                return float(result.group(1))

        def lsorbit(self):
            result = self._find_last_OUTCAR(r"""\s*LSORBIT\s*=\s*(T|F)\s+""")
            if result is not None:
                return result.group(1)

        def kpoints(self):
            from numpy import array

            result = []
            with open('OUTCAR', 'r') as file:
                found = 0
                found_generated = compile(r"""Found\s+(\d+)\s+irreducible\s+k-points""")
                found_read = compile(r"""k-points in units of 2pi/SCALE and weight""")
                for line in file:
                    if found_generated.search(line) is not None:
                        found = 1;
                        break
                    elif found_read.search(line) is not None:
                        found = 2;
                        break

            if found == 1:
                found = compile(r"""Following\s+cartesian\s+coordinates:""")
                for line in file:
                    if found.search(line) is not None: break
                for line in file:
                    data = line.split()
                    if len(data) != 4: break
                    result.append(data[:3])
            if found == 2:
                for line in file:
                    data = line.split()
                    if len(data) == 0: break
                    result.append(data[:3])
            return array(result, dtype="float64")

        def multiplicity(self):
            from numpy import array

            result = []
            found_generated = compile(r"""Found\s+(\d+)\s+irreducible\s+k-points""")
            found_read = compile(r"""k-points in units of 2pi/SCALE and weight""")
            with open("OUTCAR", 'r') as file:
                found = 0
                for line in file:
                    if found_generated.search(line) is not None:
                        found = 1; break
                    elif found_read.search(line) is not None:
                        found = 2; break
                if found == 1:
                    found = compile(r"""Following\s+cartesian\s+coordinates:""")
                    for line in file:
                        if found.search(line) is not None: break
                    file.__next__()
                    for line in file:
                        data = line.split()
                        if len(data) != 4: break;
                        result.append(data[-1])
                    return array(result, dtype="float64")
                elif found == 2:
                    for line in file:
                        data = line.split()
                        if len(data) == 0: break
                        result.append(float(data[3]))
                    return array([round(r * float(len(result))) for r in result], dtype="float64")

        def nelect(self):
            """Grep NELECT from OUTCAR"""
            # Find line like:    NELECT =      48.0000    total number of electrons
            regex = compile(r"""^\s*NELECT\s*=\s*(\S+)\s+total\s+number\s+of\s+electrons\s*$""")
            result = self._find_last_OUTCAR(regex)
            if result is None:
                raise GrepError("Could not find NELECT in OUTCAR")
            return float(result.group(1))

        def lwave(self):
            result = self._find_last_OUTCAR(r"""^\s*LWAVE\s*=\s*(\S)""")
            if result is not None:
                return result.group(1)

        def lcharg(self):
            result = self._find_last_OUTCAR(r"""^\s*LCHARG\s*=\s*(\S)""")
            if result is not None:
                return result.group(1)



        def total_energy(self):
            """Greps total energies for all electronic steps from OUTCAR."""
            from quantities import eV

            # Find line like: energy  without entropy=     -110.60314812  energy(sigma->0) =     -110.60341675
            regex = compile(r"""energy\s+without\s+entropy=\s*(\S+)\s+energy\(sigma->0\)\s+=\s+(\S+)""")
            result = self._find_last_OUTCAR(regex)
            if result is None:
                raise GrepError("Could not find total energy in OUTCAR")
            return float(result.group(1)) * eV

        def free_energy(self):
            from quantities import eV
            # Find line like: free  energy   TOTEN  =      -110.60368537 eV

            regex = compile(r"""free\s+energy\s+TOTEN\s=\s*(\S+)\s+eV""")
            result = self._find_last_OUTCAR(regex)
            if result is None:
                raise GrepError("Could not find free energy in OUTCAR")
            return float(result.group(1)) * eV

        def fermi_level(self):
            # Find line like: E-fermi :   4.1131

            regex = compile(r"""E-fermi\s\:\s*(\S+)""")
            result = self._find_last_OUTCAR(regex)
            if result is None:
                raise GrepError("Could not find fermi energy in OUTCAR")

                return float(result.group(1)) * eV

        def ispin(self):
            # Find line like: ISPIN  =      1
            regex = compile(r"""^\sISPIN\s=\s*(1|2)\s+""")
            result = self._find_last_OUTCAR(regex)
            if result is None:
                raise GrepError("Could not find ISPIN in OUTCAR")
            return int(result.group(1))

        def spin_polarized_value(self):

            with open('OUTCAR', 'r') as file:
                lines = file.readline()
            spin_comp1_re = compile(r"""\s*spin\s+component\s+(1|2)\s*$""")
            spins = [None, None]
            for i, line in enumerate(lines[::-1]):
                found = spin_comp1_re.match(line)
                if found is None: continue
                if found.group(1) == '1':
                    if spins[1] is None:
                        raise GrepError("Could not find two spin components in OUTCAR")
                    spins[0] = i
                    break
                else: spins[1] = i
            if spins[0] is None or spins[1] is None:
                raise GrepError("Could not find extract eigenvalues/occupation in OUTCAR")

        #    if self.is_dft:  ### Be careful! this part is not completed

        def unpolarized_values(self, which):
            with open('OUTCAR', 'r') as file:
                lines = file.readline()
            spin_comp1_re = compile(r"""\s*k-point\s+1\s*(\S+)\s+(\S+)\s+(\S+)\s*""")
            found = None
            for i, line in enumerate(lines[::-1]):
                found = spin_comp1_re.match(line)
                if found is not None: break
            if found is None:
                raise GrepError("Could not find fermi energy in OUTCAR")

        def eigenvalue(self):
            from numpy import array
            from quantities import eV

           # if self.ispin == 2:
           #     return array(self.)
            pass

        def halfmetallic(self):
            from numpy import max, abs
            if self.ispin == 1: return False


        def nband(self):
            # Find line like: number of bands    NBANDS=     96
            result = self._find_last_OUTCAR("""NBANDS\s*=\s*(\d+)""")
            if result is None:
                raise GrepError("Could not find NBANDS in OUTCAR")
            return int(result.group(1))


        def electropot(self):
            """Grep average atomic electrostatic potentials from OUTCAR"""
            from re import X as reX
            from numpy import array
            from quantities import eV

            with open('OUTCAR', 'r') as file:
                lines = file.readlines()
            regex = compile(r"""average\s+(electrostatic)\s+potential\s+at\s+core""", reX)

            for i, line in enumerate(lines[::-1]):
                if regex.search(line) is not None: break
                if -i + 2 > len(lines):
                    raise GrepError("Could not find average electrostatic potential in OUTCAR")
                regex = compile(r"""(?:\s|\d){8}\s*(-?\d+.\d+)""")
                result = []
                for line in lines[-i + 2:]:
                    data = line.split()
                    if len(data) == 0: break
                    result.extend([m.group(1) for m in regex.finditer(line)])

                return array(result, dtype="float64") * eV

        def dielectric_constant(self):
            # Find line like: EPSILON=  1.0000000 bulk dielectric constant

            result = self._find_last_OUTCAR("""EPSILON=\s*(\d+.\d+)\s+bulk\s+dielectric\s+constant""")
            if result is None:
                raise GrepError("Could not find dielectric constant in OUTCAR")
            return float(result.group(1))
