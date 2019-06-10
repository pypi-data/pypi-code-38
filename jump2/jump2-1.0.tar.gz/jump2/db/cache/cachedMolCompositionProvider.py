'''
Created on Nov 28, 2017

@author: Yuhao Fu
'''
from jump2.db.materials.molComposition import MolComposition
from django.core.cache import cache
import cPickle

class CachedMolCompositionProvider(object):
    """
    cache of composition.
    
    """
    def get(self, formula):
        """
        get composition.
        
        Arguments:
            formula: formula of composition. i.e. CH3CH3
        Returns:
            molComposition's object.
        """
        formula_cache='molComposition_%s' %formula
        composition=None
        if cache.has_key(formula_cache):
            composition=self._get_from_cache(formula_cache)
        elif MolComposition.objects.filter(formula=formula).exists():
            composition=self._get_from_db(formula)
            self.put(formula, composition)
        else:
            composition=self.set(formula)
        
        # initialize
        composition.prototypes=[]
        composition.structures=[]
        
        return composition
        
    def _get_from_cache(self, formula_cache):
        """
        get composition from cache.
        
        Arguments:
            formula_cache: formated formula. i.e. molComposition_CH3CH3
        """
        return cPickle.loads(cache.get(formula_cache))
    
    def _get_from_db(self, formula_cache):
        """
        get composition from database.
        
        Arguments:
            formula_cahce: formated formula. i.e. molComposition_CH3CH3
        """
        composition=MolComposition.objects.get(formula=formula_cache.split('_')[-1])
        return composition
        
    def put(self, formula, composition):
        """
        put composition in cache.
        
        Arguments:
            formula: formula of composition. i.e. CH3CH3
            composition: object of composition.
        """
        formula_cache='molComposition_%s' %formula
        cache.set(formula_cache, cPickle.dumps(composition, protocol=1), 60*30) # 30 minutes
    
    def set(self, formula, **kwargs):
        """
        add new composition to database and update the cache.
        
        Arguments:
            formula: formula of composition. i.e. CH3CH3
            
            kwargs:
                elements: collection of element's object.
                generic (optional): generalized composition. i.e. ABO3
        """
        if 'generic' in kwargs and 'elements' in kwargs:
            composition=MolComposition().create(formula, isPersist=True, generic=kwargs['generic'], elements=kwargs['elements'])
        elif 'generic' in kwargs:
            composition=MolComposition().create(formula, isPersist=True, generic=kwargs['generic'])
        elif 'elements' in kwargs:
            composition=MolComposition().create(formula, isPersist=True, elements=kwargs['elements'])
        else:
            composition=MolComposition().create(formula, isPersist=True)
        self.put(formula, composition)
        
        return composition