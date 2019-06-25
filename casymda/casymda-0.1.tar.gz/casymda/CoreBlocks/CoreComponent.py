# base class for blocks, using simpy environment's processes and time
# has environment, name, successor(s), and some more stuff
# calls visualizer if present
from simpy import Resource
from enum import Enum


class CoreComponent():

    def __init__(self, env, name, xy=None, xyContentList=None, queuing=True, ways={}, skipFlow=False, component_capacity=float('inf')):
        self.env = env  # simpy environment
        self.name = name  # string name of block (supposed to be unique)
        self.xy = xy  # coordinate of block for (entity-) animation
        self.xyContentList = xyContentList  # coordinates of the content list
        self.queuing = queuing  # bool whether visualizer should queue arriving entities
        # optional dict with waypoints to be followed by entity when flowing to successor
        self.ways = ways
        # bool to determine if entity flow to successor should be animated:
        self.skipFlow = skipFlow

        self.successors = []  # blocks to forward entities to
        self.entities = []  # list of currently processed entities
        self.visualizers = []  # list of visualizers to be called on status change
        self.overallCountIn = 0  # count overall number of entered entities
        # list of methods to call on enter (signature: component, entity)
        self.doOnEnterList = []
        # list of methods to call on exit (signature: component, entity, successor)
        self.doOnExitList = []
        self.component_resource = Resource(
            self.env, capacity=component_capacity)
        self.state = ComponentState(self)
        # wait until visualizers are set
        self.env.process(self.late_state_evaluation())

    def animate(self):
        for visualizer in self.visualizers:
            visualizer.animateComponent(self, queuing=self.queuing)

    def animateFlow(self, entity, toComp):
        for visualizer in self.visualizers:
            visualizer.animateFlow(
                self, toComp, entity, skipFlow=self.skipFlow, ways=self.ways)

    def onEnter(self, entity):
        entity.timeOfArrival = self.env.now
        self.overallCountIn += 1
        for method in self.doOnEnterList:
            method(self, entity)

    def onExit(self, entity, successor):
        self.entities.remove(entity)
        for method in self.doOnExitList:
            method(self, entity, successor)
        self.animate()
        self.animateFlow(entity, successor)

    # main entry point for entities coming from predecessors
    def processEntity(self, entity):
        self.onEnter(entity)
        yield self.env.process(self.commonProcessEntity(entity))

    # to be called for wip init of entities which already started processing
    # onEnter (incl. arrival time stamp) is omitted to account for already elapsed processing time
    def wipProcessEntity(self, entity):
        req = self.component_resource.request()
        yield req
        entity.component_resource_request = req
        self.env.process(self.commonProcessEntity(entity))

    # common behavior for both types of init
    def commonProcessEntity(self, entity):
        self.entities.append(entity)
        self.animate()
        # processing
        self.state.increment_state_count(States.busy)
        entity.currentProcess = self.env.process(self.actualProcessing(entity))
        yield entity.currentProcess  # entity.currentProcess might be used for interrupt
        # forwarding
        successor = self.findNextSuccessor(entity)
        req = successor.component_resource.request()
        self.state.increment_state_count(States.blocked)
        self.state.decrement_state_count(States.busy)
        yield req  # wait until successor is able to accept the entity
        self.state.decrement_state_count(States.blocked)
        self.component_resource.release(entity.component_resource_request)
        entity.component_resource_request = req  # remember to be released again
        self.onExit(entity, successor)
        self.env.process(successor.processEntity(entity))

    def late_state_evaluation(self):
        yield self.env.timeout(0)
        self.state.evaluate_state_count()

    def actualProcessing(self, entity):  # abstract: to be implemented by child method
        raise NotImplementedError(
            self.name + ":  actualProcessing of CoreComponent not implemented")

    def findNextSuccessor(self, entity):
        return self.successors[0]


# visualizer methods are defined in the "abstract" visualizer class (interface)
class CoreComponentVisualizer():
    def animateComponent(self, component, queuing=None, direction=None):
        raise NotImplementedError()

    def animateFlow(self, fromComp, toComp, entity, skipFlow=None, ways=None):
        raise NotImplementedError()

    def destroyEntityAnim(self, entity):
        raise NotImplementedError


class States(Enum):
    empty = "empty"
    busy = "busy"
    blocked = "blocked"


class ComponentState():

    def __init__(self, component):
        self._state_count = {state.value: 0 for state in [
            States.busy, States.blocked]}
        self._current_states = {state.value: False for state in States}
        self.component = component

    def increment_state_count(self, state):
        self._change_state_count(state, 1)

    def decrement_state_count(self, state):
        self._change_state_count(state, -1)

    def _change_state_count(self, state, change):
        self._state_count[state.value] += change
        self.evaluate_state_count()

    def evaluate_state_count(self):
        for state in [States.busy, States.blocked]:
            if self._state_count[state.value] > 0:
                self._set_current_state(state, True)
            else:
                self._set_current_state(state, False)

        if sum(self._state_count.values()) == 0:
            self._set_current_state(States.empty, True)
        else:
            self._set_current_state(States.empty, False)

    def _set_current_state(self, state, new_value):
        if self._current_states[state.value] != new_value:
            for visualizer in self.component.visualizers:
                visualizer.change_component_state(
                    self.component, state, new_value)
            self._current_states[state.value] = new_value
