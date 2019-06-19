from ethics.language import Not, And, Or, Causes, Gt, Eq, U, Impl, I, End, Means, AffectsPos, AffectsNeg, Affects, Choice, Goal, Patient, Consequence, Formula, Exists, Forall
import copy

class Branch:
    def __init__(self, formulas):
        self.formulas = []
        self.unexpanded = []
        self.formulas += formulas
        self.unexpanded += [f for f in formulas if not self.isLiteral(f)]
        self.interventions = {}
        self.varCounter = 0

    def isLiteral(self, f):
        if isinstance(f, str):
            return True
        if isinstance(f, Not) and isinstance(f.f1, str):
            return True
        return False
        
    def isLiteralBasic(self, f):
        if isinstance(f, str):
            return True
        if isinstance(f, Not) and isinstance(f.f1, str):
            return True
        return False
    
    def getLiterals(self):
        return [f for f in self.formulas if self.isLiteral(f)]
        
    def getLiteralsBasic(self):
        return [f for f in self.formulas if self.isLiteralBasic(f)]

    def firstUnexpandedNonForallFormula(self):
        for f in self.unexpanded:
            if not isinstance(f, Forall):
                return f
        return None
        
    def lastUnexpandedNonForallFormula(self):
        for f in self.unexpanded[::-1]:
            if not isinstance(f, Forall):
                return f
        return None
        
    def shortestUnexpandedNonForallFormula(self):
        form = None
        l = 0
        for f in self.unexpanded:
            if not isinstance(f, Forall) and len(str(f)) > l:
                l = len(str(f))
                form = f
        return form

    def setUnexpanded(self, formulas):
        self.unexpanded = []
        self.unexpanded += formulas
    
    def setInterventions(self, formulas):
        self.interventions = copy.deepcopy(formulas)

    def addIntervention(self, cause, effect):
        if cause not in self.interventions:
            self.interventions[cause] = []
        if effect not in self.interventions[cause]:
            self.interventions[cause] += [effect]

    def addFormula(self, formula):
        if formula not in self.formulas:
            self.formulas += [formula]
            if not self.isLiteral(formula):
                self.unexpanded += [formula]
    
    def isSaturated(self):
        for f in self.unexpanded:
            if not isinstance(f, Forall) and not self.isLiteral(f): # Forall will expand in every iteration
                return False
        return True
        
    def isClosed(self):
        for f in self.formulas:
            if Formula.getNegation(f) in self.formulas:
                self.unexpanded = [] # Saturate it 
                return True
        for k in self.interventions:
            for v in self.interventions[k]:
                if Not(v) in self.interventions[k]:
                    self.unexpanded = [] # Saturate it 
                    return True
        return False

    def generateNewVariable(self):
        self.varCounter += 1
        return "new_var_"+str(self.varCounter)

    def getAllLiteralsInFormula(self, f):
        if isinstance(f, str):
            return [f]
        elif isinstance(f, Not) and isinstance(f.f1, str):
            return [f]
        elif isinstance(f, Gt) or isinstance(f, Eq):
            if f.f1 == 0:
                return [f.f2.t1]
            elif f.f2 == 0:
                return [f.f1.t1]
        elif isinstance(f, Not):
            return self.getAllLiteralsInFormula(f.f1)
        elif isinstance(f, Consequence) or isinstance(f, Patient) or isinstance(f, Choice) or isinstance(f, I) or isinstance(f, Goal) or isinstance(f, End):
            return [f.f1]
        elif isinstance(f, Means):
            return [f.f2]
        elif isinstance(f, And) or isinstance(f, Or) or isinstance(f, Impl) or isinstance(f, Causes) or isinstance(f, Affects) or isinstance(f, AffectsPos) or isinstance(f, AffectsNeg):
            return self.getAllLiteralsInFormula(f.f1) + self.getAllLiteralsInFormula(f.f2)
        else:
            return []

    def getAllLiteralsInBranch(self):
        lits = []        
        for f in self.formulas:
            lits += self.getAllLiteralsInFormula(f)
        return list(set(lits))

    def printModel(self):
        s = ""
        types = [str, Eq, Gt, Causes, I, End, Affects, AffectsPos, AffectsNeg, Choice, Patient, Goal]
        for f in self.formulas:
            for t in types:
                if isinstance(f, t):
                    s += str(f)+" "
        return s
    
class Tableau:
    def __init__(self, formulas):
        self.branches = []
        
    def addBranch(self, branch):
        self.branches += [branch]
        
    def unsaturatedBranchExists(self):
        for b in self.branches:
            if not b.isSaturated():
                return True
        return False
        
    def openBranchExists(self):
        for b in self.branches:
            if not b.isClosed():
                return True, b
        return False, None
        
    def countOpenBranches(self):
        c = 0
        for b in self.branches:
            if b.isClosed():
                c += 1
        return c

class SatSolver:

    def satisfiable(self, formulas):
        t = Tableau(formulas)
        t.addBranch(Branch(formulas))
        while t.unsaturatedBranchExists():
            b = None
            for i in t.branches:
                if not i.isClosed() and not i.isSaturated():
                    b = i
                    break
            if b != None:
                while not b.isClosed() and not b.isSaturated():
                    f = b.firstUnexpandedNonForallFormula()
                    #f = b.lastUnexpandedNonForallFormula()
                    #f = b.shortestUnexpandedNonForallFormula()
                    #print("EXPANDING:", f, "in branch", b)
                    if isinstance(f, Not) and isinstance(f.f1, Not):
                        b.unexpanded.remove(f)
                        b.addFormula(f.f1.f1)
                    elif isinstance(f, str):
                        b.unexpanded.remove(f)
                    elif isinstance(f, Not) and isinstance(f.f1, str):
                        b.unexpanded.remove(f)
                    elif isinstance(f, I):
                        b.unexpanded.remove(f)
                    elif isinstance(f, Not) and isinstance(f.f1, I):
                        b.unexpanded.remove(f)
                    elif isinstance(f, And):
                        b.unexpanded.remove(f)
                        b.addFormula(f.f1)
                        b.addFormula(f.f2)
                    elif isinstance(f, Not) and isinstance(f.f1, Or):
                        b.unexpanded.remove(f)
                        b.addFormula(Not(f.f1))
                        b.addFormula(Not(f.f2))
                    elif isinstance(f, Or):
                        b.unexpanded.remove(f)
                        fneg1 = Formula.getNegation(f.f1)
                        fneg2 = Formula.getNegation(f.f2)
                        if fneg1 in b.formulas and fneg2 not in b.formulas:
                            b.addFormula(f.f2)   
                        elif fneg1 not in b.formulas and fneg2 in b.formulas:
                            b.addFormula(f.f1)
                        elif fneg1 not in b.formulas and fneg2 not in b.formulas:
                            b2 = Branch(b.formulas)
                            b2.setUnexpanded(b.unexpanded)
                            b2.setInterventions(b.interventions)
                            b2.addFormula(Not(f.f1))
                            b2.addFormula(f.f2)
                            t.branches += [b2]
                            b.addFormula(f.f1)
                    elif isinstance(f, Not) and isinstance(f.f1, And):
                        b.unexpanded.remove(f)
                        b.addFormula(Or(Not(f.f1.f1), Not(f.f1.f2)))
                    elif isinstance(f, Impl):
                        b.unexpanded.remove(f)
                        b.addFormula(Or(Not(f.f1), f.f2))
                    elif isinstance(f, Not) and isinstance(f.f1, Impl):
                        b.unexpanded.remove(f)
                        b.addFormula(f.f1.f1)
                        b.addFormula(Not(f.f1.f2))
                    elif isinstance(f, Causes):
                        b.unexpanded.remove(f)
                        b.addFormula(f.f1)
                        b.addFormula(f.f2)
                        b.addIntervention(f.f1, Formula.getNegation(f.f1))
                        b.addIntervention(f.f1, Formula.getNegation(f.f2))
                        b.addFormula(Or(Consequence(f.f1), Choice(f.f1)))
                        b.addFormula(Or(Consequence(f.f2), Choice(f.f2)))
                        b.addFormula(Causes(f.f1, f.f1))
                        b.addFormula(Causes(f.f2, f.f2))
                    elif isinstance(f, Not) and isinstance(f.f1, Causes):
                        b.unexpanded.remove(f)
                        b.addFormula(Or(Not(f.f1.f1), Not(f.f1.f2)))
                        b.addFormula(Or(Consequence(f.f1.f1), Choice(f.f1.f1)))
                        b.addFormula(Or(Consequence(f.f1.f2), Choice(f.f1.f2)))
                        b2 = Branch(b.formulas)
                        b2.setUnexpanded(b.unexpanded)
                        b2.setInterventions(b.interventions)
                        b2.addIntervention(f.f1.f1, Formula.getNegation(f.f1.f1))
                        b2.addIntervention(f.f1.f1, f.f1.f2)
                    elif isinstance(f, Eq): # Assumes Eq(0, U(c)) or Eq(U(c), 0)
                        b.unexpanded.remove(f)
                        if f.f1 == 0:
                            term = f.f2
                            b.addFormula(Eq(term, 0))
                        else:
                            term = f.f1
                            b.addFormula(Eq(0, term))
                        b.addFormula(Not(Gt(0, term)))
                        b.addFormula(Not(Gt(term, 0)))
                        b.addFormula(Or(Consequence(term.t1), Choice(term.t1)))
                    elif isinstance(f, Not) and isinstance(f.f1, Eq):
                        b.unexpanded.remove(f)
                        if f.f1.f1 == 0:
                            term = f.f1.f2
                        else:
                            term = f.f1.f1
                        b.addFormula(Or(Gt(0, term), Gt(term, 0)))
                        b.addFormula(Or(Consequence(term.t1), Choice(term.t1)))
                    elif isinstance(f, Gt): # Assumes Gt(0, U(c)) or Gt(U(c), 0)
                        b.unexpanded.remove(f)
                        if f.f1 == 0:
                            term = f.f2
                            b.addFormula(And(Not(Eq(0, term)), Not(Gt(term, 0))))
                        else:
                            term = f.f1
                            b.addFormula(And(Not(Eq(0, term)), Not(Gt(0, term))))
                        b.addFormula(Or(Consequence(term.t1), Choice(term.t1)))
                    elif isinstance(f, Not) and isinstance(f.f1, Gt):
                        b.unexpanded.remove(f)
                        if f.f1.f1 == 0:
                            term = f.f1.f2
                            b.addFormula(Or(Gt(term, 0), Eq(0, term)))
                        else:
                            term = f.f1.f1
                            b.addFormula(Or(Gt(0, term), Eq(0, term)))
                        b.addFormula(Or(Consequence(term.t1), Choice(term.t1)))
                    elif isinstance(f, Exists):
                        b.unexpanded.remove(f)
                        b.addFormula(Formula.substituteVariable(f.f1, b.generateNewVariable(), f.f2))
                    elif isinstance(f, Not) and isinstance(f.f1, Exists):
                        b.unexpanded.remove(f)
                        b.addFormula(Forall(f.f1.f1, Not(f.f1.f2)))
                    elif isinstance(f, Not) and isinstance(f.f1, Forall):
                        b.unexpanded.remove(f)
                        b.addFormula(Exists(f.f1.f1, Not(f.f1.f2)))
                    elif isinstance(f, End):
                        b.unexpanded.remove(f)
                        b.addFormula(Exists("_x_", And(Goal("_x_"), AffectsPos("_x_", f.f1))))
                        b.addFormula(Not(Exists("_x_", And(Goal("_x_"), AffectsNeg("_x_", f.f1)))))
                        b.addFormula(Patient(f.f1))
                    elif isinstance(f, Not) and isinstance(f.f1, End):
                        b.unexpanded.remove(f)
                        b.addFormula(Or(Not(Exists("_x_", And(Goal("_x_"), AffectsPos("_x_", f.f1.f1)))), Exists("_x_", And(Goal("_x_"), AffectsNeg("_x_", f.f1.f1)))))
                        b.addFormula(Patient(f.f1.f1))
                    elif isinstance(f, Means): # Reading-1
                        b.unexpanded.remove(f)
                        b.addFormula(Exists("_x_", Exists("_y_", And(Choice("_x_"), And(Causes("_x_", "_y_"), Affects("_y_", f.f2))))))
                        b.addFormula(Patient(f.f2))
                    elif isinstance(f, Not) and isinstance(f.f1, Means): # Reading-1
                        b.unexpanded.remove(f)
                        b.addFormula(Not(Exists("_x_", Exists("_y_", And(Choice("_x_"), And(Causes("_x_", "_y_"), Affects("_y_", f.f1.f2)))))))
                        b.addFormula(Patient(f.f1.f2))
                    elif isinstance(f, Affects):
                        b.unexpanded.remove(f)
                        b.addFormula(Or(Consequence(f.f1), Choice(f.f1)))
                        b.addFormula(Patient(f.f2))
                    elif isinstance(f, Not) and isinstance(f.f1, Affects):
                        b.unexpanded.remove(f)
                        b.addFormula(Not(AffectsPos(f.f1.f1, f.f1.f2)))
                        b.addFormula(Not(AffectsNeg(f.f1.f1, f.f1.f2)))
                        b.addFormula(Or(Consequence(f.f1.f1), Choice(f.f1.f1)))
                        b.addFormula(Patient(f.f1.f2))
                    elif isinstance(f, AffectsPos):
                        b.unexpanded.remove(f)
                        b.addFormula(Affects(f.f1, f.f2))
                        b.addFormula(Not(AffectsNeg(f.f1, f.f2)))
                        b.addFormula(Or(Consequence(f.f1), Choice(f.f1)))
                        b.addFormula(Patient(f.f2))
                    elif isinstance(f, Not) and isinstance(f.f1, AffectsPos):
                        b.unexpanded.remove(f)
                        b.addFormula(Or(Consequence(f.f1.f1), Choice(f.f1.f1)))
                        b.addFormula(Patient(f.f1.f2))             
                    elif isinstance(f, AffectsNeg):
                        b.unexpanded.remove(f)
                        b.addFormula(Affects(f.f1, f.f2))
                        b.addFormula(Not(AffectsPos(f.f1, f.f2)))
                        b.addFormula(Or(Consequence(f.f1), Choice(f.f1)))
                        b.addFormula(Patient(f.f2))
                    elif isinstance(f, Not) and isinstance(f.f1, AffectsNeg):
                        b.unexpanded.remove(f)
                        b.addFormula(Or(Consequence(f.f1.f1), Choice(f.f1.f1)))
                        b.addFormula(Patient(f.f1.f2))     
                    elif isinstance(f, Choice):
                        b.unexpanded.remove(f)
                        b.addFormula(Not(Patient(f.f1)))
                        b.addFormula(Not(Consequence(f.f1)))
                        b.addFormula(Choice(Formula.getNegation(f.f1)))
                    elif isinstance(f, Not) and isinstance(f.f1, Choice):
                        b.unexpanded.remove(f)
                        b.addFormula(Or(Patient(f.f1.f1), Consequence(f.f1.f1)))
                    elif isinstance(f, Patient):
                        b.unexpanded.remove(f)
                        b.addFormula(Not(Choice(f.f1)))
                        b.addFormula(Not(Consequence(f.f1)))
                        b.addFormula(Patient(Formula.getNegation(f.f1)))
                    elif isinstance(f, Not) and isinstance(f.f1, Patient):
                        b.unexpanded.remove(f)
                        b.addFormula(Or(Choice(f.f1.f1), Consequence(f.f1.f1)))
                    elif isinstance(f, Consequence):
                        b.unexpanded.remove(f)
                        b.addFormula(Not(Patient(f.f1)))
                        b.addFormula(Not(Choice(f.f1)))
                        b.addFormula(Consequence(Formula.getNegation(f.f1)))
                    elif isinstance(f, Not) and isinstance(f.f1, Consequence):
                        b.unexpanded.remove(f)
                        b.addFormula(Or(Patient(f.f1.f1), Choice(f.f1.f1)))
                    elif isinstance(f, I):
                        b.unexpanded.remove(f)
                        b.addFormula(Or(Consequence(f.f1), Choice(f.f1)))
                        b.addFormula(Not(I(Formula.getNegation(f.f1))))
                        b.addFormula(Exists("_x_", And(Choice("_x_"), Causes("_x_", f.f1))))
                    elif isinstance(f, Not) and isinstance(f.f1, I):
                        b.unexpanded.remove(f)
                        b.addFormula(Or(Consequence(f.f1.f1), Choice(f.f1.f1)))
                    elif isinstance(f, Goal):
                        b.unexpanded.remove(f)
                        b.addFormula(Or(Consequence(f.f1), Choice(f.f1)))
                        b.addFormula(Exists("_x_", And(Choice("_x_"), Causes("_x_", f.f1))))
                    elif isinstance(f, Not) and isinstance(f.f1, Goal):
                        b.unexpanded.remove(f)
                        b.addFormula(Or(Consequence(f.f1.f1), Choice(f.f1.f1)))
                    #for l in b.getLiteralsBasic():
                    #    b.addFormula(Causes(l, l))
                    for c in b.formulas:
                        if isinstance(c, Causes):
                            if c.f1 != c.f2:
                                b.addFormula(Not(Causes(c.f2, c.f1)))
                    for f in b.unexpanded:
                        if isinstance(f, Forall):
                            for l in b.getAllLiteralsInBranch():
                                #print("sub", f.f1, l, f.f2, b.formulas)
                                b.addFormula(Formula.substituteVariable(f.f1, l, f.f2))
                    #print(b, len(t.branches), t.countOpenBranches())
                    #print(len(t.branches), b.getAllLiteralsInBranch(), b.getLiterals(), b.unexpanded)
                    #print(len(t.branches))
        #for b in t.branches:
        #    print(b, b.formulas)
        return t.openBranchExists()
        
        
if __name__ == '__main__':
    #f = [Exists("x", Causes("a", "x")), Forall("x", Impl(Causes("a", "x"), Gt(U("x"), 0))), I("a")]
    #f = [Not(Not(Causes("a", "a"))), Not(Causes("a", "c"))]  
    #f = [Causes("a", "c1"), Causes("c1", "c2"), I("c2"), Gt(0, U("c1")), Forall("_x_", Forall("_y_", Impl(And(Causes("a", "_x_"), And(Causes("_x_", "_y_"), I("_y_"))), Not(Gt(0, U("_x_"))))))] 
    #f = [Causes("a", "c1"), Causes("c1", "c2"), I("c2"), Gt(0, U("c1")), Forall("x", Forall("y", Or(Not(Causes("a", "x")), Or(Not(Causes("x", "y")), Or(Not(I("y")), Not(Gt(0, U("x"))))))))]
    
    #f = [Causes("a", "c1"), Causes("c1", "c2"), I("c1"), Gt(0, U("c1")), Forall("x", Impl(And(Causes("a", "x"), I("x")), Not(Gt(0, U("x")))))]
    #f = [I("c1"), Not(I("c1"))]
    
    #f = [Exists("_o_", Exists("_x_", And(Goal("_x_"), AffectsPos("_x_", "_o_"))))]
    #f = [Exists("_o_", And(Means("Reading-1", "_o_"), End("_o_")))]
    #f = [Exists("_o_", And(Exists("_x_", And(Goal("_x_"), AffectsPos("_x_", "_o_"))), Not(Exists("_x_", And(Goal("_x_"), AffectsNeg("_x_", "_o_"))))))]
    f = [And(Causes('pull', 'bloody_track'), Gt(0, U('bloody_track'))), And(Causes('pull', 'human_dead'), Gt(0, U('human_dead')))]
    s = SatSolver()
    import time
    t = time.time()
    b, br = s.satisfiable(f)
    print(time.time() - t)
    print(b, None if br is None else br.printModel(), None if br is None else br.interventions)
