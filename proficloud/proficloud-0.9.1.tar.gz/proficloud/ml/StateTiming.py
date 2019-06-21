import pandas as pd
import numpy as np
from enum import Enum
from .AbstractModel import AbstractModelClass

class State():
    """
    Class representing a state.
    """

    def __init__(self, state_id, transitions, signal_thresholds):
        self.state_id = state_id
        """State ID. A unique identifier for each state"""

        self.transitions = transitions
        """Outgoing transitions to other states"""

        self.signal_thresholds = signal_thresholds
        """Learned min-max thresholds for provided signals"""
    
    def __repr__(self):
        return str(self.__dict__)

class Transition():
    """
    Class representing a transition.
    """

    def __init__(self, source_state, target_state, min_time=float("inf"), max_time=0):
        self.source_state = source_state
        """Source state ID"""

        self.target_state = target_state
        """Target state ID"""

        self.min_time = min_time
        """Minimum transition time (relative)"""

        self.max_time = max_time
        """Maximum transition time (relative)"""
    
    def __repr__(self):
        return str(self.__dict__)

class SignalThreshold():
    """
    Class to store min/max thresholds for signals.
    """

    def __init__(self, signal_name, min_value=float("inf"), max_value=0):
        self.signal_name = signal_name
        """Signal name"""

        self.min_value = min_value
        """Minimum signal value"""

        self.max_value = max_value
        """Maximum signal value"""
    
    def __repr__(self):
        return str(self.__dict__)

class AnomalyTypeEnum(Enum):
    """
    AnomalyType Enumeration. Enumerates different anomaly types.
    """

    NOT_TESTED = -1
    NO_ANOMALY = 0
    TIME_ANOMALY = 1
    STATE_ANOMALY = 2
    UNKNOWN_STATE = 3
    VALUE_ERROR = 4

class ValueErrorAnomaly():
    """
    Value error anomaly. Provides details about signal value range violations.
    """

    def __init__(self, signal_name, signal_value, signal_min_value, signal_max_value):
        self.signal_name = signal_name
        """Signal name"""

        self.signal_min_value = signal_min_value
        """Signal minumum value"""

        self.signal_max_value = signal_max_value
        """Signal maximum value"""

        self.signal_value = signal_value
        """Actual signal value"""

    def __repr__(self):
        return str(self.__dict__)

class StateTimingModelAnomaly():
    """State timing model anomaly class. Used in predict method"""

    def __init__(self):
        self.timestamp = 0
        """Absolute timestamp of anomaly"""

        self.anomaly = False
        """True on anomaly, False if everything is ok!"""

        self.anomalytype =  AnomalyTypeEnum.NOT_TESTED
        """Type of the anomaly"""

        self.source_state = None
        """Source state id of the anomaly"""

        self.target_state = None
        """Target state od of the anomaly"""

        self.relative_time = None
        """relative timing of the anomaly"""

        self.transition = None
        """transition id associated with the anomaly"""

        self.value_error = []
        """List of value errors (contains type ValueErrorAnomaly)"""

    def __repr__(self):
        return str(self.__dict__)

class StateTimingModel(AbstractModelClass):
    """
    StateTimingModel. This learns a state-machine, also called automaton, based on a given state variable and timestamp.
    This model is a normal behaviour model and detects deviations in state transitions (timing, events) and detects range violations in other provided signals.
    """

    def __init__(self):
        self.signal_names = None
        """The signal names used in this model"""

        self.state_signal_name = ""
        """The state signal name"""

        self.timestamp_signal_name = ""
        """Timestamp signal name. Must be unix-like timestamp."""

        self.states = {}
        """The states of the model (Disctionary)"""

        self.accepting_states = {}
        """The accepting states of the automaton/state machine"""

        self.maxValueOffsetFactor = 1.0
        """Offset factor for signal max value (to adjust sensitivity)"""

        self.minValueOffsetFactor = 1.0
        """Offset factor for signal min value (to adjust sensitivity)"""

        self.maxTimeOffset = 0.0
        """Time offset for relative max transition timing (to adjust sensitivity)"""

        self.minTimeOffset = 0.0
        """Time offset for relative min transition timing (to adjust sensitivity)"""

        self.initial_state = None
        """Initial state of the automaton"""

        self.debug = False
        """Enable debugging output"""

        self.current_state = -1
        """Current state during prediction"""

        self.current_time = -1
        """Current relative time during prediction"""

        self.start_time = -1
        """Absolute start time of prediction"""

        self.filter_zero_variance=False
        """Filter zero-variance signals"""

        super(AbstractModelClass, self).__init__()
    
    def train(self, data):
        
        data = data.dropna()
        
        if self.filter_zero_variance:
            variance = data.var(axis=0)
            zero_variance = variance == 0.0
            zero_variance = np.insert(zero_variance.values, 0, False)
            if sum(zero_variance) > 0:
                data = data.loc[:,~zero_variance]
        
        self.signal_names = data.columns.values.tolist()
        self.signal_names.remove(self.timestamp_signal_name)

        self.states = {}
        current_time = -1
        start_time = -1
        current_state = None

        for index, row in data.iterrows():
            timestamp = row[self.timestamp_signal_name]
            state = row[self.state_signal_name]

            if start_time < 0:
                #Initial setup
                start_time = timestamp
                current_state = state
                if self.initial_state is None:
                    self.initial_state = state

                self.states[str(current_state)] = State(current_state, {}, {})

            current_time = timestamp - start_time

            if state != current_state:
                #Transition happened
                if state not in self.states[str(current_state)].transitions:
                    self.states[str(current_state)].transitions[str(state)] = Transition(current_state, state)
                
                if self.states[str(current_state)].transitions[str(state)].min_time > current_time:
                    self.states[str(current_state)].transitions[str(state)].min_time = current_time
                
                if self.states[str(current_state)].transitions[str(state)].max_time < current_time:
                    self.states[str(current_state)].transitions[str(state)].max_time = current_time                    

                start_time = timestamp

            current_state = state

            if str(current_state) not in self.states:
                #Entered new state for the first time
                self.states[str(current_state)] = State(current_state, {}, {})

            #Update boundary values:
            for signal in self.signal_names:
                if signal == self.state_signal_name or signal == self.timestamp_signal_name:
                    continue
                
                if signal not in self.states[str(current_state)].signal_thresholds:    
                    self.states[str(current_state)].signal_thresholds[signal] = SignalThreshold(signal)
                
                val = row[signal]
                if val < self.states[str(current_state)].signal_thresholds[signal].min_value:
                    self.states[str(current_state)].signal_thresholds[signal].min_value = val
            
                if val > self.states[str(current_state)].signal_thresholds[signal].max_value:
                    self.states[str(current_state)].signal_thresholds[signal].max_value = val
        

    def resetPrediction(self):
        """Reset prediction and internal automaton state"""
        
        self.current_state = -1
        self.current_time = -1
        self.start_time = -1

    def predict(self, data):
        resultList = []
        for index,row in data.iterrows():
                result = self.predict_sample(row)
                resultList.append(result)
        return resultList

    def predict_sample(self, sample):

        result = StateTimingModelAnomaly()

        timestamp = sample[self.timestamp_signal_name]
        state = sample[self.state_signal_name]

        result.timestamp = timestamp

        if self.start_time < 0:
            #Initial setup
            self.start_time = timestamp
            if str(state) in self.states:
                self.current_state = state
            else:
                if str(self.initial_state) in self.states: 
                    self.current_state = self.initial_state
                    self.state = self.current_state
                else:
                    self.current_state = list(self.states)[0]
                    self.state = self.current_state

        self.current_time = timestamp - self.start_time

        if state != self.current_state:
            #Transition happened             
            if str(state) not in self.states[str(self.current_state)].transitions:
                if self.debug: print("STATE ANOMALY!")
                result.anomaly = True
                result.anomalytype = AnomalyTypeEnum.STATE_ANOMALY
                result.source_state = self.current_state
                result.target_state = state
                result.relative_time = self.current_time
            else:
                if ((self.states[str(self.current_state)].transitions[str(state)].min_time + self.minTimeOffset) > self.current_time
                or (self.states[str(self.current_state)].transitions[str(state)].max_time + self.maxTimeOffset) < self.current_time):
                    
                    if str(self.current_state) not in self.accepting_states:
                        if self.debug: print("TIME ANOMALY")
                        result.anomaly = True
                        result.anomalytype = AnomalyTypeEnum.TIME_ANOMALY

                result.source_state = self.current_state
                result.target_state = state
                result.relative_time = self.current_time
                result.transition = self.states[str(self.current_state)].transitions[str(state)]                    

            self.start_time = timestamp
            self.current_state = state

            if not result.anomaly:
                if str(self.current_state) not in self.states:
                    if self.debug: print("WAITING IN UNKNOWN STATE")
                    result.anomaly = True
                    result.anomalytype = AnomalyTypeEnum.UNKNOWN_STATE
                    result.source_state = self.current_state
                    result.target_state = self.current_state
                    result.relative_time = self.current_time

            #Check boundary values if there is no other anomaly detected:
            if not result.anomaly:
                for signal in self.signal_names:
                    if signal == self.state_signal_name or signal == self.timestamp_signal_name:
                        continue
                                
                    val = sample[signal]
                    if (val < (self.states[str(self.current_state)].signal_thresholds[signal].min_value * self.minValueOffsetFactor)
                    or val > (self.states[str(self.current_state)].signal_thresholds[signal].max_value * self.maxValueOffsetFactor)):
                        if self.debug: print("VALUE ERROR")
                        result.anomaly = True
                        result.anomalytype = AnomalyTypeEnum.VALUE_ERROR
                        result.source_state = self.current_state
                        result.target_state = self.current_state
                        result.relative_time = self.current_time

                        result.value_error.append(
                            ValueErrorAnomaly(signal,
                                val, 
                                self.states[str(self.current_state)].signal_thresholds[signal].min_value, 
                                self.states[str(self.current_state)].signal_thresholds[signal].max_value
                                )
                            )
        else:
            result.source_state = self.current_state
            result.target_state = self.current_state
            result.relative_time = self.current_time


        if not result.anomaly:
            result.anomalytype = AnomalyTypeEnum.NO_ANOMALY

        return result
        
    def summary(self):
        return "Simple State timing and value threshold learning and anomaly detection"
    