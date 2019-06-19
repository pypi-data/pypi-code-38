from fastscoredeploy import Model
from fastscore import Schema
import unittest
import six
import pandas as pd



class TestModel(unittest.TestCase):

    def test_model_imports(self):
        model_string = '''
# fastscore.schema.0: string
# fastscore.schema.1: int
# a comment

import json

def begin():
    global c
    c = 3

def action(x):
    global c
    yield json.loads(x) + c
        '''

        model = Model('mymodel', 'python', model_string)
        intsch = Schema(name="int", source={"type":"int"})
        strsch = Schema(name="string", source="string")

        model.schemas['int'] = intsch
        model.schemas['string'] = strsch

        self.assertEqual(model.score(["3", "4", "5"], multi_stream = False),
            [6, 7, 8])
        self.assertEqual(model.score([(0, "3"), (0, "4"), (0, "5")], multi_stream = True),
            [(1, 6), (1, 7), (1, 8)])

    def test_model_annotations(self):
        model_string = '''
# fastscore.schema.0: sch0
# fastscore.schema.1: sch1
# fastscore.recordsets.$all: yes

def action(x):
    yield x

        '''

        model = Model('mymodel', 'python', model_string)
        self.assertEqual(model.options.schema[0], 'sch0')
        self.assertEqual(model.options.schema[1], 'sch1')
        self.assertEqual(model.options.recordsets['$all'], 'yes')

        model.options.schema[3] = 'xyz'
        self.assertEqual(model.source, '''# fastscore.schema.0: sch0
# fastscore.schema.1: sch1
# fastscore.schema.3: xyz
# fastscore.recordsets.$all: yes


def action(x):
    yield x''')

    def test_model_recordsets(self):
        model_string = '''
# fastscore.schema.0: sch_in
# fastscore.schema.2: sch_in
# fastscore.schema.1: sch_out
# fastscore.recordsets.$all: yes

def begin():
    global model_params
    model_params = {'a': 1, 'b': 2}

def action(df, slot):
    if slot == 0:
        df['z'] = model_params['a']*df['x'] + model_params['b']*df['y']
    elif slot == 2:
        df['z'] = model_params['a']*df['x'] - model_params['b']*df['y']
    yield df
        '''
        model = Model('mymodel', 'python', model_string)
        sch_in = Schema(name='sch_in', source=
                {"type":"record",
                 "name":"sch_in",
                 "fields":[
                     {"name":"x", "type":"double"},
                     {"name":"y", "type":"double"}
                 ]})
        sch_out = Schema(name='sch_out', source=
                 {"type":"record",
                  "name":"sch_out",
                  "fields":[
                      {"name":"x", "type":"double"},
                      {"name":"y", "type":"double"},
                      {"name":"z", "type":"double"}]
                 })

        model.schemas['sch_in'] = sch_in
        model.schemas['sch_out'] = sch_out
        mydf = pd.DataFrame({'x':[1.0, 2.0, 3.0], 'y':[4.0, 5.0, 6.0]})

        score0 = list(model.score([(0, mydf)], multi_stream=True)[0][1]['z'])
        self.assertEqual(score0, [9.0, 12.0, 15.0])
        score1 = list(model.score([(2, mydf)], multi_stream=True)[0][1]['z'])
        self.assertEqual(score1, [-7.0, -8.0, -9.0])

    class MockEngine(object):
        class ActiveStream(object):
            def detach(self):
                return

        def __init__(self):
            self.active_streams = { 0: TestModel.MockEngine.ActiveStream()}

        def load_model(self, model, dry_run = False):
            return
        def verify_schema(self, schema):
            return 1
        def unverify_schema(self, index):
            return
        def attach_stream(self, stream, slot, dry_run = False):
            return
        def reset(self):
            return


    class MockModelManage(object):
        def __init__(self):
            self.schemas = {'sch_in': 1, 'sch_out': 2}
        def save_stream(self, stream):
            return
        def save_model(self, model):
            return
        def save_schema(self, schema):
            return



    def test_model_deployment(self):
        engine = TestModel.MockEngine()
        mm = TestModel.MockModelManage()
        model_string = '''
# fastscore.schema.0: sch_in
# fastscore.schema.1: sch_out

# fastscore.recordsets.$in: yes

def action(df):
    yield df.mean()['x']
        '''
        model = Model(name='mymodel', mtype='python',
            source=model_string, model_manage=mm)
        sch_in = Schema(name = "sch_in", source={"type":"int"})
        sch_out = Schema(name = "sch_out", source={"type":"double"})
        model.schemas['sch_in'] = sch_in
        model.schemas['sch_out'] = sch_out
        model.deploy(engine)
