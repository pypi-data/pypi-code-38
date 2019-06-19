
from ethics.language import *

def makeSetOfAlternatives(*models):
    for m in models:
        m.setAlternatives(*models)
        
def makeSetOfEpistemicAlternatives(*models):
    for m in models:
        m.setEpistemicAlternatives(*models)
        m.probability = 1/len(models)
        

def mapBackToFormulae(l, m): # l: model, m: map
    erg = []
    for ll in l:
        found = False
        for mm in m:
            if m[mm] == ll:
                try:
                    erg.append(eval(mm).nnf())
                except:
                    erg.append(mm)
                found = True
                break
        if(found == False):
            for mm in m:
                if m[mm] + ll == 0:
                    try:
                        erg.append(Not(eval(mm)).nnf())
                    except:
                        erg.append(Not(mm).nnf())
                    break
    return erg
