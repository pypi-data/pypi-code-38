import struct
from pyparsing import Regex, Literal, Optional, oneOf, ParseException
from iotile.core.exceptions import *
from .fw_stream import SensorStream

#Constants that need to be synced with firmware on devices
trigger_ops = {'>': 0, '<': 1, '>=': 2, '<=': 3, '=': 4, '==': 4, 'always': 5}
# Include new and old names where appropriate
processor_list = {'copyA': 0, 'copy_latest_a': 0,
                  'averageA': 1,
                  'copyAllA': 2, 'copy_all_a': 2,
                  'sumA': 3,
                  "copyCountA": 4, 'copy_count_a': 4,
                  "triggerStreamer": 5, 'trigger_streamer': 5,
                  "call_tile": 6, 'call_rpc': 6,
                  "subtract_afromb": 7}

#DSL Language Definition
symbol_names = " ".join(processor_list.keys())

number = Regex('((0x[a-fA-F0-9]+)|[0-9]+)').setParseAction(lambda s,l,t: [int(t[0], 0)])
combiner = (Literal('&&') | Literal('||')).setParseAction(lambda s,l,t: [t[0] == '||']) # True when disjunction
symbol = oneOf(symbol_names).setParseAction(lambda s,l,t: [processor_list[t[0]]])

stream_type = Optional(Literal('system')) + (Literal('input') | Literal('output') | (Literal('buffered') + Optional(Literal('node').suppress())) | (Literal("unbuffered") + Optional(Literal('node').suppress())) | Literal("constant") | (Literal("counter")  + Optional(Literal('node').suppress())))
stream = stream_type + number

trigger_type = (Literal('value') | Literal('count')).setParseAction(lambda s,l,t: [t[0] == 'value']) # True when trigger is based on value data
trigger_op = oneOf('> < >= <= = ==').setParseAction(lambda s,l,t: [trigger_ops[t[0]]])

trigger = Literal('always') | (Literal('when').suppress() + trigger_type('type') + trigger_op + number)

inputstring = stream + trigger

inputdesc2 = Literal('(').suppress() + inputstring('inputA') + combiner('combiner') + inputstring('inputB') + Literal(')').suppress()
inputdesc1 = Literal('(').suppress() + inputstring('inputA') + Literal(')').suppress()

inputdesc = inputdesc1('input1') | inputdesc2('input2')
graph_node = inputdesc + Literal('=>').suppress() + stream('node') + Literal('using').suppress() + symbol('processor')


class SensorGraphNode:
    def __init__(self, desc):
        if not isinstance(desc, str):
            raise ValidationError("attempting to create a SensorGraphNode without using a string description", description=desc)

        try:
            data = graph_node.parseString(desc)
        except ParseException as e:
            raise ValidationError("invalid node descriptor that could not be parsed", location=e.loc, reason=e.msg)
        self.trigger_combiner = 0
        if 'combiner' in data:
            self.trigger_combiner = int(data['combiner'])

        self.inputA = SensorStream(0xFFFF)
        self.triggerA = self._process_trigger({}, 0)
        self.inputB = SensorStream(0xFFFF)
        self.triggerB = self._process_trigger({}, 0)
        self.ascii = desc

        if 'inputA' in data:
            count = 2
            if data['inputA'][0] == 'system':
                count = 3
            self.inputA = SensorStream(" ".join(map(str, data['inputA'][:count])))
            self.triggerA = self._process_trigger(data['inputA'], count+1)

        if "inputB" in data:
            count = 2
            if data['inputB'][0] == 'system':
                count = 3

            self.inputB = SensorStream(" ".join(map(str, data['inputB'][:count])))
            self.triggerB = self._process_trigger(data['inputB'], count+1)

        count = 2
        if data['node'][0] == 'system':
            count = 3

        self.stream = SensorStream(" ".join(map(str, data['node'][:count])))

        self.processor = data['processor']

    def _process_trigger(self, inputdesc, offset):
        """
        Create an 8-bit trigger op and extract the trigger data
        """

        if "type" not in inputdesc:
            return (trigger_ops['always'] << 1, 0)

        use_value = inputdesc['type']

        if use_value:
            return (inputdesc[offset+0] << 1, inputdesc[offset+1])

        return ((1 | (inputdesc[offset+0] << 1)), inputdesc[offset+1])

    def describe_trigger(self, input):
        if input == 0:
            trig = self.triggerA
        else:
            trig = self.triggerB

        value = trig[1]
        cond = trig[0]

        desc = {}
        desc['value'] = value

        if cond & (0b1):
            desc['type'] = 'count'
        else:
            desc['type'] = 'value'

        op = cond >> 1

        ops = {y:x for x, y in trigger_ops.items()}
        desc['op'] = ops[op]

        if desc['op'] == 'always':
            desc['type'] = 'always'

        return desc

    def create_descriptor(self):
        """
        Create a packed binary description of this sensor graph node suitable for sending to an IOTile controller
        """

        #This packed binary format is defined in lib_controller: firmware/src/sensor_graph/sensor_graph.h => sg_node_definition_t (20 bytes long)
        #L: trigger value A
        #L: trigger value B
        #H: stream
        #H: input A stream
        #H: input B stream
        #B: processor
        #B: trigger cond A
        #B: trigger cond B
        #B: trigger combiner
        #B: reserved
        #B: reserved
        return struct.pack("<LLHHHBBBBBB", self.triggerA[1], self.triggerB[1], self.stream.id, self.inputA.id, self.inputB.id, self.processor, self.triggerA[0], self.triggerB[0], self.trigger_combiner, 0, 0)

    def __str__(self):
        out = "SensorGraphNode\n"
        out += "  inputA: %d\n" % self.inputA.id
        out += "  inputB: %d\n" % self.inputB.id
        out += "  stream: %d\n" % self.stream.id
        out += "  processor: %d\n" % self.processor

        return out

def convert(arg):
    if isinstance(arg, SensorGraphNode):
        return arg

    return SensorGraphNode(arg)

def default_formatter(arg, **kwargs):
    return str(arg)
