import witchcraft
from witchcraft.combinators import *
from witchcraft.utils import build_tuple_type
from witchcraft.dateutil.parser import parse as dateutil_parse
from witchcraft.upsert import detect_type, get_data_types,preprocess_csv_data
import unittest
from sqlsession import SqlSession
from owl.load import load_text_data


test_database = {
  'user':     'owl',
  'password': 'owl',
  'host':     'localhost',
  'port':     '5432',
  'database': 'spookyowl_demo',
  'type':     'pgsql'

}

class Test(unittest.TestCase):
    
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init_tuple(self):
        T = build_tuple_type(['one', 'two', 'three'])
        d = {'one': 1, 'two': 2, 'three': 3}

        td = T(d)
        self.assertDictEqual(td.asdict(), d)

        td = T([('one', 1), ('two', 2), ('three', 3)])
        self.assertDictEqual(td.asdict(), d)

        td = T(**d)
        self.assertDictEqual(td.asdict(), d)
        td = T(d, ['one', 'two', 'three'])

        self.assertDictEqual(td.asdict(), d)

    def test_select_columns(self):
        select_columns({'one': 1, 'two': 2, 'three': 3}, 
                             [('two', 'dva')])


    def test_dateutil(self):

        with open('stimulus/payment_10k.csv', encoding='windows-1250') as input_file:
            decoded_data = input_file.read()
            
            f_header, header, data = preprocess_csv_data(decoded_data)
            result, types = get_data_types(header, data)
            print(types)
        

if __name__ == '__main__':
    unittest.main()
    
