import json
import io
from itertools import combinations, chain
from ethics.language import *

class Model(object):
    """ Models """
    def __init__(self):
        self.probability = None
        self.alternatives = []
        self.epistemic = []
        self.checker = None

    def models(self, formula):
        return self.checker.models(self, formula)
        
    def degBelief(self, formula):
        p = 0
        for e in self.epistemic:
            if e.models(formula):
                p = p + e.probability
        return p

    def setAlternatives(self, *alternatives):
        self.alternatives = alternatives

    def getAlternatives(self, f=None):
        if f == None:
            return self.alternatives
        r = []
        for w in self.alternatives:
            if w.models(f):
                r.append(w)
        return r

    def setEpistemicAlternatives(self, *alternatives):
        self.epistemic = alternatives

    def getEpistemicAlternatives(self, f=None):
        if f == None:
            return self.epistemic
        r = []
        for w in self.epistemic:
            if w.models(f):
                r.append(w)
        return r

    def setProbability(self, p):
        self.probability = p


class Checker(object):
    """
    Checker
    """
    def models(self, model, formula):
        pass

    def _trueInEveryAlternative(self, model, formula):
        for m in model.epistemic:
            if not m.models(formula):
                return False
        return True

"""
Causal Networks
"""


class CausalModel(Model):
    """
    Representation of models in accordance
    to Definition 2.
    """
    def __init__(self, file, world):
        super(CausalModel, self).__init__()
        self.file = file
        with io.open(file) as data_file:
            self.model = json.load(data_file)
            # Actions are mandatory
            self.actions = [str(a) for a in self.model["actions"]]
            # Optional entries
            try:
                self.utilities = {str(k): v for k, v in self.model["utilities"].items()}
            except:
                self.utilities = {}
            try:
                self.patients = [str(a) for a in self.model["patients"]] 
            except: 
                self.patients = []
            try:
                self.description = str(self.model["description"])
            except:
                self.description = "No Description"
            try:
                self.consequences = [str(c) for c in self.model["consequences"]]
            except:
                self.consequences = []
            try:
                self.background = [str(b) for b in self.model["background"]]
            except:
                self.background = []
            try:
                self.mechanisms = {str(k): eval(v) for k, v in self.model["mechanisms"].items()}
            except:
                self.mechanisms = {}
            self._computeNetwork()
            try:
                self.intentions = {str(k): list(map(str, v)) for k, v in self.model["intentions"].items()}
            except:
                self.intentions = {}
            try:
                self.goals = {str(k): list(map(str, v)) for k, v in self.model["goals"].items()}
            except:
                self.goals = {}
            try:
                self.affects = {str(k): v for k, v in self.model["affects"].items()}
            except: 
                self.affects = {}
            
        self.domainOfQuantification = self.actions + self.consequences + [Not(x) for x in self.consequences + self.actions + self.background] + self.background + self.patients
        self.consequenceLiterals = self.consequences + [Not(x) for x in self.consequences]
        self.world = world
        self.intervention = {}
        self.checker = CausalModelChecker()
        self._setAction()
        
    def getModelAsConjunction(self):
        m = []
        # Literals
        v = self.consequences + self.actions + self.background + [Not(x) for x in self.consequences + self.actions + self.background]
        lits = [c if self.models(c) else Not(c) for c in v]
        # Good, Bad, Neutral
        m += [Good(x) if self.models(Good(x)) else Not(Good(x)) for x in v]
        m += [Bad(x) if self.models(Bad(x)) else Not(Bad(x)) for x in v]
        m += [Neutral(x) if self.models(Neutral(x)) else Not(Neutral(x)) for x in v]
        m += [Better(x,y) if self.models(Better(x,y)) else Not(Better(x,y)) for x in self.actions for y in self.actions]
        m += [Causes(x,y) if self.models(Causes(x,y)) else Not(Causes(x,y)) for x in v for y in v]
        m += [I(x) if self.models(I(x)) else Not(I(x)) for x in v]
        m += lits
        return Formula.makeConjunction(m)

    def setUtilities(self, u):
        self.utilities = u

    def clearIntervention(self):
        self.intervention = {}
        
    def powerset(self, i):
        """
        Generates the subsets of consequences to be held fixed. 
        See https://www.ijcai.org/Proceedings/15/Papers/427.pdf,
        Definition AC2(a^m) 
        """
        return chain.from_iterable(combinations(i, r) for r in range(len(i)+1))

    def setFlippedIntervention(self, variables):
        """ For Halpern-like But-for causality """
        for variable in variables:
            currValue = self.models(variable)
            if isinstance(variable, str):
                self.intervention[variable] = not currValue
            elif isinstance(variable, Not):
                self.intervention[variable.f1] = currValue

    def setInterventionWithVariablesFixedToOriginal(self, variables):
        """ For the modified Halpern-Pearl Causality """
        intervention_backup = self.intervention
        intervention_new = {}
        self.clearIntervention()
        for v in variables:
            currValue = self.models(v)
            if isinstance(v, str):
                intervention_new[v] = currValue
            elif isinstance(v, Not):
                intervention_new[v] = not currValue
        self.intervention = dict(list(intervention_backup.items()) + list(intervention_new.items()))

    def setNewIntervention(self, intervention):
        self.clearIntervention()
        for v in intervention:
            if isinstance(v, str):
                self.intervention[v] = True
            elif isinstance(v, Not):
                self.intervention[v.f1] = False

    def _addToNetwork(self, v, k):
        if v in self.network:
            if k not in self.network[v]:
                self.network[v].append(k)
        else:
            self.network[v] = []
            if k not in self.network[v]:
                self.network[v].append(k)

    def _computeNetwork(self):
        self.network = {}
        for k, v in self.mechanisms.items():
            if isinstance(v, str):
                self._addToNetwork(v, k)
            else:
                parents = v.stripParentsFromMechanism()
                for p in parents:
                    self._addToNetwork(p, k)

    def path(self, a, b, v):
        if a == [b]:
            return True
        if b in a:
            return True
        for x in [z for z in a if z not in v]:
            if x in self.network:
                a.extend(self.network[x])
            v.append(x)
            return self.path(a, b, v)
        return False

    def _setAction(self):
        self.action = [a for a in self.actions if self.world[a] == 1][0]

    def getDirectConsequences(self):
        return [c for c in self.consequences if self.models(Causes(self.action, c))] + [Not(c) for c in self.consequences if self.models(Causes(self.action, Not(c)))]
        
    def getDirectBadConsequences(self):
        direct = self.getDirectConsequences()
        return [c for c in direct if self.models(Gt(0, U(c)))]
        
    def getAllBadConsequences(self):
        cons = self.getAllConsequences()
        return [c for c in cons if self.models(Gt(0, U(c)))]

    def getAllConsequences(self):
        return [c if self.models(c) else Not(c) for c in self.consequences]
        
    def evaluate(self, principle):
        try:
            p = principle(self)
        except:
            p = principle
        perm = p.permissible()
        return perm
        
    def explain(self, principle):
        try:
            p = principle(self)
        except:
            p = principle
        return p.explain()
        
    def __checkProbabilities(self, k):
        for m in k:
            if self.probability is None:
                self.__setDefaultProbabilities(k)
                return
    
    def __setDefaultProbabilities(self, k):
        prob = 1/len(k)
        for m in k:
            m.probability = prob
        
    def degPerm(self, principle):
       k_a = self.getEpistemicAlternatives(f=self.action)
       self.__checkProbabilities(k_a)
       prob_sum = 0.0
       prob_perm = 0.0
       for w in k_a:
           p = w.evaluate(principle)
           if p is True or p is False:
               prob_sum = prob_sum + w.probability
           if p is True:
               prob_perm = prob_perm + w.probability
       if prob_sum > 0.0:
           return prob_perm/prob_sum
       return "Not Applicable"

    def __repr__(self):
        return str(self.model)
        

    def groundForall(self, formula):
        f = None
        for e in self.domainOfQuantification:
            s = Formula.substituteVariable(formula.f1, e, formula.f2)
            if f is None:
                if isinstance(s, Exists):
                    f = self.groundExists(s)
                elif isinstance(s, Forall):
                    f = self.groundForall(s)
                else:
                    f = s
            else:
                if isinstance(s, Exists):
                    f = And(self.groundExists(s), f)
                elif isinstance(s, Forall):
                    f = And(self.groundForall(s), f)
                else:
                    f = And(s, f)
        return f
        
    def groundExists(self, formula):
        f = None
        for e in self.domainOfQuantification:
            s = Formula.substituteVariable(formula.f1, e, formula.f2)
            if f is None:
                if isinstance(s, Exists):
                    f = self.groundExists(s)
                elif isinstance(s, Forall):
                    f = self.groundForall(s)
                else:
                    f = s
            else:
                if isinstance(s, Exists):
                    f = Or(self.groundExists(s), f)
                elif isinstance(s, Forall):
                    f = Or(self.groundForall(s), f)
                else:
                    f = Or(s, f)
        return f
        
    def ground(self, formula):
        if isinstance(formula, And):
            return And(self.ground(formula.f1), self.ground(formula.f2))
        if isinstance(formula, Or):
            return Or(self.ground(formula.f1), self.ground(formula.f2))
        if isinstance(formula, Impl):
            return Impl(self.ground(formula.f1), self.ground(formula.f2))
        if isinstance(formula, BiImpl):
            return BiImpl(self.ground(formula.f1), self.ground(formula.f2))
        if isinstance(formula, Not):
            return Not(self.ground(formula.f1))
        if isinstance(formula, Exists):
            return self.groundExists(formula)
        if isinstance(formula, Forall):
            return self.groundForall(formula)
        return formula
            


class CausalModelChecker(Checker):
    """
    Implementation of Definition 8
    """

    def _intended(self, intentions, formula):
        if isinstance(formula, str):
            return formula in intentions
        if isinstance(formula, Not):
            return str(formula) in intentions
        if isinstance(formula, And):
            return self._intended(intentions, formula.f1) and self._intended(intentions, formula.f2)
        return False
        
    def _affects(self, affects, formula, posneg):
        if isinstance(formula, str):
            return formula in [i[0] for i in affects if i[1] == posneg]
        if isinstance(formula, And):
            return self._affects(affects, formula.f1) and self._affects(affects, formula.f2)
        return False

    def evaluateTerm(self, model, term):
        if isinstance(term, int):
            return term
        if isinstance(term, Minus):
            return -1*self.evaluateTerm(term.f1)
        if isinstance(term, Add):
            return self.evaluateTerm(term.t1) + self.evaluateTerm(term.t2)
        if isinstance(term, Sub):
            return self.evaluateTerm(term.t1) - self.evaluateTerm(term.t2)
        if isinstance(term, U):
            return self._sumUp(model, term.t1)
        if isinstance(term, DR):
            return self._computeDR(model, term.t1, term.t2)
        if isinstance(term, DB):
            return self._computeDB(model, term.t1, term.t2)
            
    def _computeDB(self, model, t1, t2):
        """ Degree of Blame """
        r = 0
        for w in model.epistemic:
            r = r + w.probability * w.checker._computeDR(model, t1, t2)
        return r

    def _computeDR(self, model, t1, t2):
        """ Degree of Responsibility """
        b, c = self._partialCause(model, PCauses(t1, t2))
        if not b:
            return 0
        else:
            b, w = self._findWitness(model, Causes(c, t2))
            return 1/len(w)

    def _sumUp(self, model, formula):
        if formula is None:
            return 0
        if isinstance(formula, bool):
            return 0
        if isinstance(formula, str):
            if formula in model.utilities:
                return model.utilities[formula]
            else:
                return 0
        if isinstance(formula, Not):
            if isinstance(formula.f1, str):
                if str(formula) in model.utilities:
                    return model.utilities[str(formula)]
                else:
                    return 0
            if isinstance(formula.f1, Not):
                return self._sumUp(model, formula.f1.f1)
        if isinstance(formula, And):
            return self._sumUp(model, formula.f1) + self._sumUp(model, formula.f2)

    def _allAreIndirectParents(self, model, p, e):
        """ accepts single variables, events formulae, or collections """
        if isinstance(p, str):
            pLit = [p]
        elif isinstance(p, Formula):
            pLit = p.getPosLiteralsEvent()
        else:
            pLit = list(p)
        eLit = [e] if isinstance(e, str) else e.getPosLiteralsEvent()
        for l1 in pLit:
            found = False
            for l2 in eLit:
                if model.path([l1], l2, []):
                    found = True
                    break
            if not found:
                return False
        return True

    def _findWitness(self, model, formula):
        # Let's Go!
        # Compute the intervention, i.e., in boolean case we 
        # flip the value of the variables mentioned in the maybe-cause.
        maybeCause = [formula.f1] if isinstance(formula.f1, str) else formula.f1.getAllLiteralsEvent()
        model.setFlippedIntervention(maybeCause)
        # Now we have to check if we can find a set of variables, 
        # such that if we keep their value fixed to the value they have in the current world,
        # then the caused formula evaluates to false.
        for w in model.powerset([c for c in model.consequences if c not in maybeCause]):
            # It makes no sense to consider variables that are not at least indirect parents.
            # The empty witness is okay, though.
            if len(w) == 0 or self._allAreIndirectParents(model, w, formula.f2):
                # Intervention: Fixing values.
                model.setInterventionWithVariablesFixedToOriginal(w)
                # Evaluate the caused formula in the new world.
                check = self.models(model, formula.f2)
                # That's it, now we can delete the intervention.
                model.clearIntervention()
                # So, if 'check' is True then our (maybeCause, w) is no witness of the cause.
                # But if 'check' is False then we have found something that at least contains a cause.
                # What remains then is to check if a subset of variables could also be a cause.  
                if check == False:
                # In case the cause is a single conjunct it must be a minimal cause.
                    if isinstance(formula.f1, str):
                        return True, maybeCause+list(w)
                    # Otherwise we check if there is some smaller subset of the cause that also is a cause.
                    found = False
                    for s in model.powerset(maybeCause):
                        if len(s) > 0 and len(s) < len(maybeCause):
                            f = Formula.makeConjunction(s)
                            if model.models(Causes(f, formula.f2)):
                                found = True
                                break
                    # No smaller subset of the cause has been identified as a cause.
                    # Thus, our cause really is a minimal cause.
                    if found == False:
                        return True, maybeCause+list(w)
        return False, []

    def _partialCause(self, model, formula):
        if self.models(model, Causes(formula.f1, formula.f2)):
            return True, formula.f1
        lits = model.background+model.actions+model.consequences
        allLit = [e for e in lits if self.models(model, e)]
        allLit = allLit + [Not(e) for e in lits if not self.models(model, e)]
        formulaLit = [formula.f1] if isinstance(formula.f1, str) else formula.f1.getAllLiteralsEvent()
        l = [e for e in allLit if e not in formulaLit]
        for x in model.powerset(l):
            f = Formula.makeConjunction(x)
            if f != None:
                if self.models(model, Causes(And(formula.f1, f), formula.f2)):
                    return True, And(formula.f1, f)
        return False, None

    def _sufficientCauseInEveryModel(self, model, f1=None, f2=None):
        w_f = model.getEpistemicAlternatives(f=And(f1, f2))
        for w in w_f:
            if not w.models(SCauses(f1, f2)):
                return False
        return True
                    
    def models(self, model, formula):
        if isinstance(formula, bool):
            return formula
        if isinstance(formula, str):
            if formula in model.intervention:
                return model.intervention[formula]
            if formula in model.world:
                return model.world[formula]
            if formula in model.consequences:
                return self.models(model, model.mechanisms[formula])
        if isinstance(formula, Not):
            return not self.models(model, formula.f1)
        if isinstance(formula, Or):
            return self.models(model, formula.f1) or self.models(model, formula.f2)
        if isinstance(formula, And):
            return self.models(model, formula.f1) and self.models(model, formula.f2)
        if isinstance(formula, Impl):
            return not self.models(model, formula.f1) or self.models(model, formula.f2)
        if isinstance(formula, Impl):
            return self.models(model, And(Impl(formula.f1, formula.f2), Impl(formula.f2, formula.f1)))
        if isinstance(formula, I):
            if model.action not in model.intentions:
                return False
            return self._intended(model.intentions[model.action], formula.f1)
        if isinstance(formula, Affects):
            return self._affects(model.affects[formula.f1], formula.f2, "+") or self._affects(model.affects[formula.f1], formula.f2, "-")
        if isinstance(formula, AffectsPos):
            return self._affects(model.affects[formula.f1], formula.f2, "+")
        if isinstance(formula, AffectsNeg):
            return self._affects(model.affects[formula.f1], formula.f2, "-")
        if isinstance(formula, Causes):
            # Condition A1: Cause and caused must hold.
            if self.models(model, formula.f1) and self.models(model, formula.f2):
                # Just for performance reasons, let's deal with very simple cases directly.
                if formula.f1 == formula.f2:
                    return True
                if formula.f1 == Not(formula.f2) or Not(formula.f1) == formula.f2:
                    return False
                if not self._allAreIndirectParents(model, formula.f1, formula.f2):
                    return False
                b, w = self._findWitness(model, formula)
                if b:
                    return True
            return False
        if isinstance(formula, PCauses):
            b, c = self._partialCause(model, formula)
            return b
        if isinstance(formula, SCauses):
            # Condition SC1
            if not self.models(model, formula.f1) or not self.models(model, formula.f2):
                return False
            # Condition SC2
            conj = [formula.f1] if isinstance(formula.f1, str) else formula.f1.getAllLiteralsEvent()
            b_c = False
            for c in conj:
                if self.models(model, PCauses(c, formula.f2)):
                    b_c = True
                    break
            if b_c == False:
                return False
            # Condition SC3
            if not self.models(model, K(Intervention(formula.f1, formula.f2))):
                return False
            # Condition SC4
            if isinstance(conj, str):
                return True
            found = False
            for s in model.powerset(conj):
                if len(s) > 0 and len(s) < len(conj):
                    f = Formula.makeConjunction(s)
                    if model.models(SCauses(f, formula.f2)):
                        found = True
                        break
            # No smaller subset of the cause has been identified as a sufficient cause.
            # Thus, our scause really is a minimal scause.
            if found == False:
                return True
            return False
        if isinstance(formula, Prevents):
            prevented = [formula.f2] if isinstance(formula.f2, str) else formula.f2.getAllLiteralsEvent()
            for e in prevented:
                if isinstance(e, str):
                    f = Not(e)
                else:
                    f = e.f1
                if self.models(model, Causes(formula.f1, f)):
                    return True
            return False
        if isinstance(formula, Explains):
            # EX1
            if not self._sufficientCauseInEveryModel(model, f1=formula.f1, f2=formula.f2):
                return False
            # EX2
            conj = [formula.f1] if isinstance(formula.f1, str) else formula.f1.getAllLiteralsEvent()
            if not isinstance(conj, str):
                for w in model.powerset(conj):
                    if len(w) > 0 and len(w) < len(conj):
                        ff = Formula.makeConjunction(w)
                        if self._sufficientCauseInEveryModel(model, f1=ff, f2=formula.f2):
                            return False
            # EX3
            if len(model.getEpistemicAlternatives(f=And(formula.f1, formula.f2))) == 0:
                return False
            # EX4
            if not self.models(model, Not(K(formula.f1))):
                return False
            return True
        if isinstance(formula, Intervention):
            i = [formula.f1] if isinstance(formula.f1, str) else formula.f1.getAllLiteralsEvent()
            model.setNewIntervention(i)
            b = self.models(model, formula.f2)
            model.clearIntervention()
            return b
        if isinstance(formula, Eq):
            return self.evaluateTerm(model, formula.f1) == self.evaluateTerm(model, formula.f2)
        if isinstance(formula, Gt):
            return self.evaluateTerm(model, formula.f1) > self.evaluateTerm(model, formula.f2)
        if isinstance(formula, GEq):
            return self.evaluateTerm(model, formula.f1) >= self.evaluateTerm(model, formula.f2)
        if isinstance(formula, Good):
            return self.evaluateTerm(model, U(formula.f1)) > 0
        if isinstance(formula, Bad):
            return self.evaluateTerm(model, U(formula.f1)) < 0
        if isinstance(formula, Neutral):
            return self.evaluateTerm(model, U(formula.f1)) == 0
        if isinstance(formula, Better):
            # Compute Overall Utility of f1
            world1 = dict(model.world)
            for x in world1.keys():
                if x == formula.f1:
                    world1[x] = True
                else:
                    world1[x] = False
            cm1 = CausalModel(model.file, world1)
            u1 = self._sumUp(model, Formula.makeConjunction(cm1.getAllConsequences()))
            
            # Compute Overall Utility of f2
            world1 = dict(model.world)
            for x in world1.keys():
                if x == formula.f2:
                    world1[x] = True
                else:
                    world1[x] = False
            cm1 = CausalModel(model.file, world1)
            u2 = self._sumUp(model, Formula.makeConjunction(cm1.getAllConsequences()))
            
            return u1 > u2
        if isinstance(formula, K):
            return self._trueInEveryAlternative(model, formula.f1)
        if isinstance(formula, Goal):
            return formula.f1 in model.goals[model.action]
        if isinstance(formula, Choice):
            return self.action == formula.f1
        if isinstance(formula, Patient):
            return formula.f1 in model.patients
        if isinstance(formula, End):
            foundPos = False
            for i in model.goals[model.action]:
                if self.models(model, AffectsNeg(i, formula.f1)):
                    return False
                if not foundPos and self.models(model, AffectsPos(i, formula.f1)):
                    foundPos = True
            return foundPos
        if isinstance(formula, Means):
            for i in [model.action]+model.getDirectConsequences():
                if formula.f1 == "Reading-1":
                    for g in model.goals[model.action]:
                        if self.models(model, And(Causes(i, g), Affects(i, formula.f2))):
                            return True
                if formula.f1 == "Reading-2":
                    if self.models(model, Affects(i, formula.f2)):
                        return True
            return False
        if isinstance(formula, Forall):
            f = model.groundForall(formula)
            return self.models(model, f)
        if isinstance(formula, Exists):
            f = model.groundExists(formula)
            return self.models(model, f)
        if isinstance(formula, Consequence):
            return formula.f1 in model.consequences
    

