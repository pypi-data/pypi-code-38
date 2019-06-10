#coding=utf-8
'''
Created on Dec 11, 2017

@author: Yuhao Fu
'''
# for database
def initialize_relationships(structure):
    """
    initialize according to the data in the database.
        
    根据数据库中的数据，初始化结构对象。注意：当从数据库中提取结构时，需要对提取的结构对象执行初始化操作，使内存中的structure等类中的属性数组初始化。
    """
    # composition
    composition=structure.composition
    composition.structures.append(structure)
    composition.elements=structure.elements
    
    # atom
    for atom in structure.atoms:
        element=structure.get_element(atom.element.symbol)
        element.atoms.append(atom)
        if not atom.species is None:
            species=structure.get_species(atom.species.name)
            species.atoms.append(atom)
    # species
    for species in structure.species:
        species.element=structure.get_element(species.element.symbol)
        species.structures.append(structure)
        element=structure.get_element(species.element.symbol)
        element.species.append(species)
    # element
    for element in structure.elements:
        element.structures.append(structure)
        element.compositions.append(structure.composition)