import unittest
import random

from networktools.library import (random_char,
                                  my_random_string,
                                  complete_nro,
                                  hextring,
                                  hextring2int,
                                  check_type,
                                  get_command,
                                  all_variants,
                                  reverse_dict,
                                  multikey,
                                  multivalue,
                                  pattern_value,
                                  key_on_dict,
                                  check_gsof,
                                  gns_loads,
                                  gns_dumps,
                                  context_split,
                                  geojson2angularjson,
                                  geojson2rethinkjson,
                                  geojson2json)
"""
Checked:

random_char
my_random_string
"""

class TestStrFunctions(unittest.TestCase):
    def test_random_char(self):
        max_test=100
        nums = list(range(48,58))
        alfab = list(range(65,91))
        chars = nums + alfab
        x = random_char()
        list_chars = [random_char() for n in range(random.randint(0,max_test))]
        list_verify = [len(x) == 1 for x in list_chars]
        check = all(list_verify)
        list_verify_char = [ord(x) in chars for x in list_chars if len(x) == 1]
        check_char = all(list_verify_char)
        check_final = check and check_char
        self.assertTrue(check_final)

    def test_my_random_string(self):
        max_test = 1000
        list_numeric = [random.randint(4, n) for n in range(5,random.randint(10, max_test))]
        list_rd_strings = [my_random_string(x) for x in list_numeric]
        list_verify = [x == y for x,y in zip(map(len, list_rd_strings), list_numeric)]
        check = all(list_verify)
        self.assertTrue(check)

    def test_complete_nro(self):
        max_numbers = 200
        random_numbers = [random.randint(0,n) for n in range(random.randint(0,max_numbers))]
        max_complete = 20
        random_complete = [random.randint(0,n) for n in range(random.randint(0,max_complete))]
        # run fn, complete a value with n chars (0)
        complete_this =  lambda x, list_numbers: [complete_nro(x, n=n) for n in list_numbers]
        # create the same with std
        template = lambda n: "{value:0%dd}" %n
        complete_this_compare =  lambda x, list_numbers: [template(n).format(value=x) for n in list_numbers]
        lista_complete_nro = [complete_this(x,random_complete) for x in random_numbers ]
        len_lcn = [len(row) for row in lista_complete_nro]
        lista_complete_check = [complete_this_compare(x,random_complete) for x in random_numbers ]
        len_lcch = [len(row) for row in lista_complete_check]
        compare_lens = all([x==len_lcch[i] for i,x in enumerate(len_lcn)])
        chec_lists = False
        if compare_lens:
            compare_atom = lambda row1, row2: all([len(x)==len(row2[i]) for i, x in enumerate(row1)])
            check_lists = all([compare_atom(row1, lista_complete_check[i])
                               for i, row1 in enumerate(lista_complete_nro)])
        check = compare_lens and check_lists
        self.assertTrue(check)

    def test_hextring(self):
        max_test = 1000
        list_numeric = [random.randint(0, n) for n in range(0,random.randint(0, max_test))]
        list_hextr = [hextring(x) for x in list_numeric]
        list_recover = [format(n, 'x') for n in list_numeric]
        check = all([x == list_recover[i] for i,x in enumerate(list_hextr)])
        self.assertTrue(check)

    def test_hextring3int(self):
        max_test = 1000
        list_numeric = [random.randint(0, n) for n in range(0,random.randint(0, max_test))]
        list_hextr = [hextring(x) for x in list_numeric]
        list_recover = [hextring2int(hx) for hx in list_hextr]
        check = all([x==list_recover[i] for i,x in enumerate(list_numeric)])
        self.assertTrue(check)

    def test_check_type_boolean(self):
        trues = {'true', 't', 'T',
                 'True', 'verdadero',
                 '1', 's', 'S', 'Si', 'si', 1, True}
        falses = {'falso', 'false', 'False',
                  'f', '0', 'n', 'N', 'No', 'no', '', 0, False}
        trues.remove(True)
        falses.remove(False)
        dtrues = dict.fromkeys(trues, True)
        dfalses = dict.fromkeys(falses, False)
        dict_check = {}
        dict_check.update(dtrues)
        dict_check.update(dfalses)
        check = all([value is check_type(inp) for inp, value in dict_check.items()])
        self.assertTrue(check)

    def test_check_type_int(self):
        type_check = 'int'
        max_test = 1000
        list_numeric = [random.randint(4, n) for n in range(5,random.randint(10, max_test))]
        list_rd_strings = [my_random_string(x) for x in list_numeric]
        [list_rd_strings.append(val) for val in ['021','2323232','1231231','6562143231']]
        check_list_digit = [word.isdigit() for word in list_rd_strings]
        lista_result_true = [i for i,n in enumerate(check_list_digit) if n]
        check = all([type(check_type(list_rd_strings[i], tipo=type_check)) is int
                     for i in lista_result_true])
        self.assertTrue(check)

    def test_check_type_real(self):
        type_check = {'double', 'float', 'real'}
        numbers = ['121212.12','124132.123123','123213.12312312','2132168.123',
                   '-123213.512312',
                   '-613.2000000000000123']
        check_list = []
        for tp in type_check:
            check = all([type(check_type(n, tipo=tp)) is float
                                 for n in numbers])
            check_list.append(check)
        check = all(check_list)
        self.assertTrue(check)

    def test_multikey(self):
        commands = {
            'ala':'PAJARO',
            'pata':'PERRO',
            'aleta':'PEZ'
        }
        variantes = {'ala':{
                        'ala',
                        'Ala',
                        'alA',
                        'ALA',},
                     'pata':{
                        'pata',
                        'Pata',
                        'paTa',
                        'patA',},
                     'aleta':{
                        'aleta',
                        'Aleta',
                        'aLeta',
                        'alEta',
                        'aleTa',
                        'aletA'}
        }
        check_list = []
        for key, value in commands.items():
            case_check = []
            for variante in variantes.get(key):
                result, final_key, command = multikey(commands, variante)
                fk= final_key == key
                check = all([result, fk, command==value ])
                case_check.append(check)
            check = all(case_check)
            check_list.append(check)
        check=all(check_list)
        self.assertTrue(check)

    def test_all_variants(self):
        max_test = 100
        list_numeric = [random.randint(4, n) for n in range(5,random.randint(10, max_test))]
        list_rd_strings = [my_random_string(x) for x in list_numeric]
        # check number of variants: 2^n
        len_of_words = [len(w) for w in list_rd_strings]
        amount_variants = [2**n for n in len_of_words]
        len_variants = [len(all_variants(w)) for w in list_rd_strings]
        check=all([len_w == len_variants[i] for i,len_w in len_of_words])
        self.assertTrue(check)

    def test_multivalue(self):
        commands = {
            'ala':'PAJARO',
            'pata':'PERRO',
            'aleta':'PEZ'
        }
        rev_comm = reverse_dict(commands)
        values = {
            'PAJARO':all_variants('ala'),
            'PERRO':all_variants('pata'),
            'PEZ':all_variants('aleta')
        }
        check = True
        self.assertTrue(check)
