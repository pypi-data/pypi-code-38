import itertools
import json
import io
import copy
import time

class Action:
    """Representation of an endogeneous action"""
    def __init__(self, name, pre, eff, intrinsicvalue):
        """Constructor of an action
        
        Keyword arguments:
        name -- Label of the action
        pre -- Preconditions of the action
        eff -- (Conditional) Effects of the action
        intrinsicvalue -- Intrinsic moral value of the action as required by deontological principles
        """
        self.name = name
        self.pre = pre
        self.eff = eff
        self.intrinsicvalue = intrinsicvalue
        
    def __str__(self):
        """String representation of an action"""
        return self.name
        
class Event:
    """Representation of an event"""
    
    def __init__(self, name, pre, eff, times = None):
        """Constructor of an event
        
        Keyword arguments:
        name -- Label of the event
        pre -- Preconditions of the event
        eff -- (Conditional) Effects of the event
        times -- Time points at which the event will (try to) fire
        """
        self.name = name
        self.pre = pre
        self.eff = eff
        if times == None:
            times = []
        self.times = times
        
class Plan:
    """Representation of an action plan"""
    
    def __init__(self, endoPlan):
        """Constructor of an action plan
        
        Keyword arguments:
        endoPlan -- List of (endogeneous) actions
        """
        self.endoActions = endoPlan
        
    def __str__(self):
        """String representation of an action plan"""
        s = "["
        for a in self.endoActions:
            s += str(a) + ","
        return s+"]"

    def __repr__(self):
        """Representation of an action object"""
        return self.__str__()

class Situation:
    """Representation of a situation"""
    
    def __init__(self, json = None):
        """Constructor of a situation.
        
        Keyword arguments:
        json -- JSON file containing the description of the situation
        """
        if json == None:
            self.actions = None
            self.events = None
            self.init = None
            self.goal = None
            self.affects = None
            self.utilities = None
        else:
            self.parseJSON(json)

        self.alethicAlternatives = []
        self.epistemicAlternatives = []
        self.creativeAlternatives = []

        self.eventcounter = 0

    def cloneSituation(self):
        """Build a new situation which equals the current situation."""
        return Situation(self.jsonfile)
 
    def parseJSON(self, jsonfile):
        """Build a situation from a JSON file. Used by the constructor.
        
        Keyword arguments:
        jsonfile -- The JSON file to be loaded.
        """
        self.jsonfile = jsonfile
        with io.open(jsonfile) as data_file:
            data = json.load(data_file)
            self.actions = []
            for a in data["actions"]:
                action = Action(a["name"], a["preconditions"], a["effects"], a["intrinsicvalue"])
                self.actions += [action]
            self.events = []
            for a in data["events"]:
                event = Event(a["name"], a["preconditions"], a["effects"], a["timepoints"])
                self.events += [event]
            self.affects = data["affects"]
            self.goal = data["goal"]
            self.init = data["initialState"]
            planactions = []
            for a in data["plan"]:
                for b in self.actions:
                    if a == b.name:
                        planactions += [b]
            self.plan = Plan(planactions)
            self.utilities = data["utilities"]

    def getNumberOfEvents(self):
        n = 0
        for e in self.events:
            n += len(e.times)
        return n
    
    def getHarmfulConsequences(self):
        "Retrieve all consequences of the action plan, which have negative utility."""
        allCons = self.getAllConsequences()
        harmful = []
        for u in self.utilities:
            if u["utility"] < 0:
                if self.isSatisfied(u["fact"], allCons):
                    harmful += [u["fact"]]  
        return harmful  

    def getHarmfulFacts(self):
        """Retrieve all harmful facts"""
        harmful = []
        for u in self.utilities:
            if u["utility"] < 0:
                harmful += [u["fact"]]
        return harmful

    def getNegation(self, fact):
        """Get the Negation of the fact"""
        v = list(fact.values())[0]
        return {list(fact.keys())[0]:not v}

    def getGenerallyAvoidableHarmfulFacts(self):
        """Retrieve all harmful facts for which there is a plan, whose execution does not result in the fact to be true."""
        avoidable = []
        sit = self.cloneSituation()
        for h in sit.getHarmfulFacts():
            nh = sit.getNegation(h)
            sit.goal = nh
            plan = sit.generatePlan()
            if plan != False:
                avoidable += [h]
        return avoidable
    
    def getAllConsequences(self):
        """Retrieve all consequences of the action plan, i.e., the final state."""
        return self.simulate()

    def getUtility(self, fact):
        """Retrieve the utility of a particular fact.
        
        Keyword arguments:
        fact -- The fact of interest
        """
        for u in self.utilities:
            if fact == u["fact"]:
                return u["utility"]
        return 0

    def getFinalUtility(self):
        """Retrieve aggregated utility of the final state."""
        utility = 0
        sn = self.simulate()
        for k, v in sn.items():
            utility += self.getUtility({k:v})
        return utility
        
    def isInstrumentalAt(self, effect, positions):
        """Determine if the goal is reached also if some effect is blocked at particular positions of the execution.
        
        Keyword arguments:
        effect -- The effect to block (a fact)
        positions -- An array of bits representing for each endogeneous action in the plan if the introduction of the effect shall be blocked or not.
        """
        sn = self.simulate(blockEffect = effect, blockPositions = positions)
        return not self.satisfiesGoal(sn)    
        
    def isInstrumental(self, effect):
        """Determine if an effect is instrumental, i.e., if blocking this effect somewhere during plan execution will render the goal unachieved."""
        for p in self.getSubPlans(len(self.plan.endoActions)):
            if self.isInstrumentalAt(effect, p):
                return True
        return False
        
    def treatsAsEnd(self, p):
        """A moral patient p is treated as an end iff it is positively and not negatively affected by some goal.
        
        Keyword arguments:
        p -- The moral patient
        """
        for e in self.affects[p]["neg"]:
            if self.isSatisfied(e, self.goal):
                return False
        for e in self.affects[p]["pos"]:
            if self.isSatisfied(e, self.goal):
                return True
        return False
        
    def treatsAsMeans(self, p, reading = 1):
        """A moral patient p is treated as a means iff p is affected by some instrumental effect.
        
        Keyword arguments:
        p -- The moral patient
        """
        for e in self.affects[p]["pos"] + self.affects[p]["neg"]:
            if reading == 1 and self.isInstrumental(e):
                return True
            if reading == 2 and self.agentivelyCaused(e):
                return True
        return False
        
    def agentivelyCaused(self, effect):
        """Check if some given effect is caused by the agent's actions.
        
        Keyword arguments:
        effect -- The effect
        """
        sn = self.simulate()
        if not self.isSatisfied(effect, sn):
            return False
        for e in self.getSubEvents():
            sne = self.simulate(skipEvents = e)
            if self.isSatisfied(effect, sn):
                for p in self.getSubPlans():
                    sn = self.simulate(skipEndo = p, skipEvents = e)
                    if not self.isSatisfied(effect, sn):
                        return True
        return False
        
    def isSufficient(self, skip, effect):
        """Check if some actions are sufficient for the effect to finally occur.
        
        Keyword arguments:
        skip -- actions to skip
        effect -- The effect
        """
        sn = self.simulate(skipEndo=[not b for b in skip])
        if self.isSatisfied(effect, sn):
            return True
        return False
        
        
    def sub(self, c, d):
        x = []
        for i in range(len(c)):
            x.append(c[i] - d[i])
        if 1 in x and -1 not in x:
            return True
        return False
    
    def minimalSets(self, cand):
        mins = []
        for c in cand:
            found = False
            for d in cand:
                if self.sub(c, d): # detect non-minimal
                    found = True
            if not found:
                mins.append(c)
        return mins
                    
    
    def getMinSufficient(self, effect):
        """Search for minimal sets of actions sufficient for the effect to finally occur.
        
        Keyword arguments:
        effect -- The effect
        """
        sn = self.simulate()
        if self.isSatisfied(effect, sn):
            cand = []
            for p in self.getSubPlans():
                if self.isSufficient(p, effect):
                    cand.append(p)
            return self.minimalSets(cand)
        return None
        
    def isNecessary(self, skip, effect):
        """Check if some actions are necessary for the effect to finally occur.
        
        Keyword arguments:
        skip -- actions to skip
        effect -- The effect
        """
        sn = self.simulate()
        if self.isSatisfied(effect, sn):
            sn = self.simulate(skipEndo=skip)
            if not self.isSatisfied(effect, sn):
                return True
        return False
   
   
    def getMinNecessary(self, effect):
        """Search for minimal sets of actions sufficient for the effect to finally occur.
        
        Keyword arguments:
        effect -- The effect
        """
        sn = self.simulate()
        if self.isSatisfied(effect, sn):
            cand = []
            for p in self.getSubPlans():
                if self.isNecessary(p, effect):
                    cand.append(p)
            return self.minimalSets(cand)
        return None
        
    def evaluate(self, principle, *args):
        """Check if the situation is permissible according to a given ethical principle.
        
        Keyword arguments:
        principle -- The ethical principle
        """
        if len(args) > 0:
            return principle(args).permissible(self)
        return principle().permissible(self)
            
    def isApplicable(self, action, state):
        """Check if an action is applicable in a given state.
        
        Keyword arguments:
        action -- The action
        state -- The state
        """
        return self.isSatisfied(action.pre, state)
        
    def apply(self, action, state, blockEffect = None):
        """Apply an action to a state. Possibly block some of the action's effect.
        
        Keyword arguments:
        action -- The action to apply
        state -- The state to apply the action to
        blockEffect -- An effect to be blocked as an effect of the action (Default: None).
        """
        if blockEffect == None:
            blockEffect = {}
        if self.isApplicable(action, state):
            si = copy.deepcopy(state)
            for condeff in action.eff:
                if self.isSatisfied(condeff["condition"], si):
                    for v in condeff["effect"].keys():
                        if not v in blockEffect or blockEffect[v] != condeff["effect"][v]:    
                            state[v] = condeff["effect"][v]
        return state

    def applyAllEvents(self, state, events, time, skip):
        """Simulatneously, apply all applicable events to a state.
           
        Keyword arguments:
        state -- The current state to apply all events to
        events -- List of all events
        time -- Point in time
        skip -- Bit string representing which of the events to be skipped.
        """
        eventlist = [e for e in events if (time in e.times and self.isApplicable(e, state))]
        si = copy.deepcopy(state)
        for e in eventlist:
            for condeff in e.eff:
                if self.isSatisfied(condeff["condition"], state):
                    for v in condeff["effect"].keys():
                        if skip == None or skip[self.eventcounter] == 0:
                            si[v] = condeff["effect"][v]
            self.eventcounter += 1
        return si
    
    def isSatisfied(self, partial, state):
        """Check if some partial state is satisfied in some full state.
        
        Keyword arguments:
        partial -- Partial state (e.g., a condition)
        state -- Full state
        """
        for k in partial.keys():
            if k not in state or partial[k] != state[k]:
                return False
        return True
        
    def satisfiesGoal(self, state):
        """Check if a state is a goal state.
        
        Keyword arguments:
        state -- state to check for goal state
        """
        return self.isSatisfied(self.goal, state)
           
    def lastExo(self):
        """Compute the last event to fire. Used for the simulation to make sure, events after the last action will also be invoked."""
        m = 0
        for e in self.events:
            if max(e.times) > m:
                m = max(e.times)
        return m
        
    def getSubPlans(self, n = None):  
        """Computes all bit strings of length n. These are intended to be used as representing for each of the n steps in the plan, whether or not it is included in a subplan.
        
        Keyword arguments:
        n -- Length of the bit string (Default: None). If None, then n is set to the length of the complete plan.
        """     
        if n == None:
            n = len(self.plan.endoActions)
        return itertools.product([1, 0], repeat=n)

    def getSubEvents(self, n = None):
        """Computes all bit strings of length n. These are intended to be used as representing for each of the n events, whether or not it should be considered.
        
        Keyword arguments:
        n -- Length of the bit string (Default: None). If None, then n is set to the number of events.
        """
        if n == None:
            n = self.getNumberOfEvents()
        return itertools.product([0, 1], repeat=n)

    def simulate(self, skipEndo = None, skipEvents = None, blockEffect = None, blockPositions = None):
        """ Simulate a plan in a situation
        
        Keyword arguments:
        init -- The initial State
        skipEndo -- A list of bits representing for each endogeneous action in the plan whether or not to execute it.
        skipEvents -- A list of bits representing for each events whether or not to execute it.
        blockEffect -- An effect to counterfactually not been added to a successor state at actions specified in blockPositions.
        blockPositions -- Positions in the plan where the blockEffect should be blocked (given as a list of bits, one for each endogeneous action in the plan).
        """
        self.eventcounter = 0
        init = copy.deepcopy(self.init)
        if skipEndo == None:
            skipEndo = [0]*len(self.plan.endoActions)
        if blockEffect == None:
            blockEffect = {}
        if blockPositions == None:
            blockPositions = [0] * len(self.plan.endoActions)
        cur = init
        for t in range(len(self.plan.endoActions)):
            if not skipEndo[t]:
                if blockPositions[t] == 1:
                    cur = self.apply(self.plan.endoActions[t], cur, blockEffect)
                else:
                    cur = self.apply(self.plan.endoActions[t], cur)
            """
            for e in self.events:
                if t in e.times:
                    cur = self.apply(e, cur) # Assumes that there is at most one event per t!
            """
            cur = self.applyAllEvents(cur, self.events, t, skipEvents)
        if self.lastExo() >= len(self.plan.endoActions):
            for t in range(len(self.plan.endoActions), self.lastExo()+1):
                cur = self.applyAllEvents(cur, self.events, t, skipEvents)
                """      
                for e in self.events:
                    if t in e.times:
                        cur = self.apply(e, cur) # Assumes that there is at most one event per t!
                """
        return cur
    
    def generatePlan(self, frontier = None, k = 10, principle = None):
        """A very simple action planner.
        
        Keyword arguments:
        frontier -- The frontier of the current search (Default: None)
        k -- Maximum plan length, for performance reasons (Default: 10)
        principle -- Ethical principle the final plan should satisfy (Default: None)
        """
        if k == 0:
            return False
        if frontier == None:
            frontier = [Plan([])]
            # Maybe the empty plan already does the job
            s = self.planFound(frontier[0], principle)
            if s != False:
                return s
        for a in self.actions:
            newplancand = Plan(frontier[0].endoActions+[a])
            s = self.planFound(newplancand, principle)
            if s != False:
                return s
            frontier += [newplancand]
        return self.generatePlan(frontier[1:], k - 1, principle)

    def planFound(self, newplancand, principle):
        """Check if a new plan has been found. Used by generatePlan.
        
        Keyword arguments:
        newplancand -- New candidate plan to be checked
        principle -- Ethical principle to evaluate the plan
        """
        newsit = Situation(self.jsonfile)
        newsit.plan = newplancand
        fstate = newsit.simulate()
        if self.satisfiesGoal(fstate):
            if principle == None or principle().permissible(newsit):
                return newsit
        return False    

    def generateCreativeAlternative(self, principle):
        """Generates a permissible alternative to the current situation.
           
           Keyword arguments:
           principle -- Ethical principle the plan of the new situation should satisfy.
        """
        for c in self.creativeAlternatives:
            c.plan = (c.generatePlan(principle = principle)).plan
            if c.plan != False:
                return c
        return False

    def makeMoralSuggestion(self, principle, *args):
        """A procedure to come up with a suggestion as to how
           to respond to a presented solution to a moral dilemma.
           Case 1: The presented solution is permissible according to
                   the ethical principle. Then everything is fine.
           Case 2: Case 1 does not hold. Therefore, a better plan is
                   searched for.
           Case 3: Case 1 does not hold and the search in Case 2 is
                   unsuccessful. A counterfactual alternative situation is 
                   constructed which meets the requirements of the ethical principle.
           
           Keyword arguments:
           principle -- The ethical principle to use to judge the situation
        """
        # Maybe the situation is alright as is
        if principle(args).permissible(self):
            return self
        # Maybe just the plan is bad and we can find a better one
        p = self.generatePlan(principle = principle)
        if p != False:
            sit = self.cloneSituation()
            sit.plan = p.plan
            if principle(args).permissible(sit):
                return sit
        # Otherwise, let's be creative
        return self.generateCreativeAlternative(principle)
        
    def models(formula):
        pass
        

"""
Ethical Principles
"""

class Deontology:
    def __init__(self, *args):
        """Empty constructor"""
        pass

    def permissible(self, situation):
        """The situation is permissible iff no action in the plan is intrinsically bad.
        
        Keyword arguments:
        situation -- The situation
        """
        for a in situation.plan.endoActions:
            if a.intrinsicvalue == "bad":
                return False
        return True


class AvoidAnyHarm:
    def __init__(self, *args):
        """Empty constructor"""
        pass
        
    def permissible(self, situation):
        """The situation is permissible iff there are no harmful consequences in the final state.
                
        Keyword arguments:
        situation -- The situation
        """
        return len(situation.getHarmfulConsequences()) == 0


class AvoidAvoidableHarm:
    def __init__(self, *args):
        """Empty constructor"""
        pass

    def permissible(self, situation):
        """The situation is permissible iff any harmful consequence in the final state could not have been avoided by any plan.

        Keyword arguments:
        situation -- The situation
        """
        hc = situation.getHarmfulConsequences()
        hf = situation.getGenerallyAvoidableHarmfulFacts()
        for h in hc:
            if h in hf:
                return False
        return True
            

class DoNoHarm:
    def __init__(self, *args):
        """Empty constructor"""
        pass
        
    def permissible(self, situation):
        """The situation is permissible iff if there is harm in the final state then it's not caused by the agent's actions.
                
        Keyword arguments:
        situation -- The situation
        """
        for h in situation.getHarmfulConsequences():
            causes = situation.agentivelyCaused(h)
            if causes:
                return False
        return True


class DoNoInstrumentalHarm:
    def __init__(self, *args):
        """Empty constructor"""
        pass
        
    def permissible(self, situation):
        """The situation is permissible iff if there is harm in the final state then it's not contributing to the agent's goal, i.e., is just a side effect.
                
        Keyword arguments:
        situation -- The situation
        """
        for h in situation.getHarmfulConsequences():
            if situation.isInstrumental(h):
                return False
        return True


class KantianHumanity:
    def __init__(self, *args):
        """Constructor for the Humanity principle.
        
        Arguments:
        reading -- indicate whether reading 1 or reading 2 shall be used (Default: 1).
        """
        if len(args) == 0:
            self.reading = 1
        else:
            self.reading = args[0][0]
        
    def permissible(self, situation):
        """The situation is permissible iff all moral patients used as a means are also used as an end.
                
        Keyword arguments:
        situation -- The situation
        """
        for p in situation.affects.keys():
            if situation.treatsAsMeans(p, self.reading) and not situation.treatsAsEnd(p):
                return False
        return True


class Utilitarianism:
    def __init__(self, *args):
        """Empty constructor"""
        pass
        
    def permissible(self, situation):
        """The situation is permissible iff there is no alternative which yields more overall utility.
                
        Keyword arguments:
        situation -- The situation
        """
        u = situation.getFinalUtility()
        for a in situation.alethicAlternatives:
            if a.getFinalUtility() > u:
                return False
        return True


class DoubleEffectPrinciple:
    def __init__(self, *args):
        """Empty constructor"""
        pass
        
    def permissible(self, situation):
        """The situation is permissible iff
           1) it is permissible according the deontology
           2) No goal fact is bad and there is at least one good goal fact
           3) it is permissible according to instrumental harm
           4) Overall utility of the final state is positive
                
        Keyword arguments:
        situation -- The situation
        """
        # Deontology
        if not Deontology().permissible(situation):
            return False, "deon"
        # No bad goals, one good one
        foundgood = False
        for k,v in situation.goal.items():
            if situation.getUtility({k:v}) < 0:
                return False, "bad goal"
            if situation.getUtility({k:v}) > 0:
                foundgood = True
        if not foundgood:
            return False
        # No bad means
        if not DoNoInstrumentalHarm().permissible(situation):
            return False
        # All in all positive
        return situation.getFinalUtility() > 0

