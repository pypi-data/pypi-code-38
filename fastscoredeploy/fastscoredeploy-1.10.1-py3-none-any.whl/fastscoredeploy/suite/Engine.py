from fastscore.suite import Engine as BaseEngine
from ..codec.datatype import jsonNodeToAvroType
from ..codec import to_json, from_json, recordset_from_json
import json
from fastscore import FastScoreError

class Engine(BaseEngine):
    """
    An Engine instance.
    """

    def __init__(self, name):
        """
        Constructor for the Engine class.

        Generally, this is not intended to be constructed 'by hand'. Instead,
        Engine instances should be retrieved from Connect.

        :param name: A name for this instance.

        """
        super(Engine, self).__init__(name)
        self._outbuffer = []

    @classmethod
    def from_base(self, baseengine):
        return Engine(baseengine.name)

    def score(self, data, encode=True):
        """
        Scores the data on the currently running model. Requires the input and
        output streams to use the REST transport.

        >>> engine.score(data=[1,2,3])
        [4,5,6]
        >>> engine.score(data=['1', '2', '3'], encode=False)
        ['4', '5', '6']

        :param data: The data to score, e.g. a list of JSON records.
        :param encode: A boolean indicating whether to encode the inputs. If
            True, the input data is encoded to JSON, and the output is decoded
            from JSON.
        :returns: The scored data.
        """
        if self.state != 'RUNNING':
            raise FastScoreError("Engine is not running (no model deployed).")

        active_streams = self.active_streams
        transport_0 = active_streams[0].descriptor['Transport']
        if (type(transport_0) == dict and 'Type' in list(transport_0.keys()) and transport_0['Type'] != 'REST') and transport_0 != 'REST':
            raise FastScoreError("Input stream must use REST transport.")
        transport_1 = active_streams[1].descriptor['Transport']
        if (type(transport_1) == dict and 'Type' in list(transport_1.keys()) and transport_1['Type'] != 'REST') and transport_1 != 'REST':
            raise FastScoreError("Output stream must use REST transport.")

        active_model = self.active_model
        input_schema = jsonNodeToAvroType(active_model.slots[0].schema)
        output_schema = jsonNodeToAvroType(active_model.slots[1].schema)

        input_recordsets = active_model.slots[0].recordsets
        output_recordsets = active_model.slots[1].recordsets

        inputs = []
        if not encode:
            inputs = [x for x in data]
        else:
            inputs = [x for x in to_json(data, input_schema)]
            if input_recordsets:
                inputs += ['{"$fastscore":"set"}']

        input_str = ''
        for datum in inputs:
            input_str += datum.strip() + '\n'
        input_str += '{"$fastscore":"pig"}\n'

        # now we send the input
        self.input(data=input_str, slot=0)

        # TODO: Simple mode
        # map(lambda x: self.input(x, slot=0), inputs)

        # send the outputs
        pig_received = False

        outputs = []

        while not pig_received:
            output = self.output(slot=1) # returns bytes
            while output is None:
                output = self.output(slot=1) # returns bytes
            if isinstance(output, bytes):
                output = output.decode('utf-8')
            outputs = outputs + [x for x in output.split('\n') if len(x) > 0]
            if {"$fastscore": "pig"} in [json.loads(x) for x in outputs]:
                pig_received = True

        # TODO: simple mode
        # outputs = []
        # output = self.output(slot=1)
        # while output is not None:
        #    output = self.output(slot=1)
        #    outputs.append(output)

        if not encode:
            return outputs
        else:
            if json.loads(outputs[-1]) == {"$fastscore": "pig"}:
                outputs = outputs[:-1]
            if json.loads(outputs[-1]) == {"$fastscore": "set"}:
                outputs = outputs[:-1]
            if output_recordsets:
                return recordset_from_json(outputs, output_schema)
            else:
                return [x for x in from_json(outputs, output_schema)]
