
import os, commands, re
import numpy as np
        
class TotalEnergy(object):

    def __init__(self):
        
        self.__energies = None
        self.__version = None
	
    def total_energies(self, path):
        """
        Get the total electronic energy of each structure.

        return a dict{'type':'ionic', 'energy':[(free, without_entropy, sigma)]} 
        """
        
        indir = os.path.join(path,'OUTCAR')
        
        # temp file % 
        command = 'grep -A4 "FREE ENERGIE OF THE ION-ELECTRON SYSTEM" {inp}'

        content = commands.getoutput(command.format(inp=indir))
       	content = re.findall(r"=(?=)+\s*(\d+\.?\d+|\S+)",content)
        energy = np.float64(content) 
        energy = energy.reshape(3, len(content)/3) 
        
        self.__energies = energy


    def get_free_energies(self):
	"""
	return free energy of all the structures
        """ 
        energy = self.__energies
        
        return energy.T[0]
            
        
    def get_free_energies_without_entropy(self):
	"""
	return free energy of all the structures without entropy
        """ 
        energy = self.__energies
        
        return energy.T[1]

    def get_free_energies_sigma(self):
	"""
	return free energy of all the structures when sigma->0
        """ 
        energy = self.__energies
        
        return energy.T[2]

    def get_final_energy(self):
	"""
	return final energy of the last structure 
        """ 
        energy = self.__energies
        types= ['free_energy', 'no_entropy','sigma0']

        return dict(zip(types, energy[-1]))
    
    @property
    def final_energy(self):
	
        energy = self.get_final_energy()

          
#a=TotalEnergy()
#a.total_energies('.') 
#print '------> free E', a.get_free_energies()
#print '------> no entroy', a.get_free_energies_without_entropy()
#print '------> sigma0', a.get_free_energies_sigma()
#print '------> final energy', a.get_final_energy()
