import unittest
import tempfile
import shutil
import os
from tios import utilities

class TestCheckMethods(unittest.TestCase):

    def setUp(self):
        self.testdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.testdir)

    def test_id_generator(self):
        result1 = utilities.id_generator()
        result2 = utilities.id_generator()
        self.assertNotEqual(result1, result2)

    def test_check_md_code_from_string_with_nothing(self):
        result = utilities.md_code_from_string('')
        self.assertEqual(result, None)

    def test_check_md_code_from_string_with_gmx(self):
        result = utilities.md_code_from_string('mpirun gmx mdrun -deffnm test')
        self.assertEqual(result, 'GROMACS')

    def test_check_md_code_from_string_with_gmx_d(self):
        result = utilities.md_code_from_string('mpirun gmx_d mdrun -deffnm test')
        self.assertEqual(result, 'GROMACS')

    def test_check_md_code_from_string_with_sander(self):
        result = utilities.md_code_from_string('mpirun sander -O -i test.in')
        self.assertEqual(result, 'AMBER')

    def test_check_md_code_from_string_with_pmemd(self):
        result = utilities.md_code_from_string('mpirun pmemd -O -i test.in')
        self.assertEqual(result, 'AMBER')

    def test_check_md_code_from_string_with_pmemd_MPI(self):
        result = utilities.md_code_from_string('mpirun pmemd.MPI -O -i test.in')
        self.assertEqual(result, 'AMBER')

    def test_check_md_code_from_string_with_pmemd_then_gmx(self):
        result = utilities.md_code_from_string('mpirun pmemd -O -i gmx')
        self.assertEqual(result, 'AMBER')

    def test_check_md_code_from_string_with_pmemd_then_gmx_index(self):
        code, result = utilities.md_code_from_string('mpirun pmemd -O -i gmx', index=True)
        self.assertEqual(result, 1)

    def test_check_md_code_from_string_with_namd(self):
        result = utilities.md_code_from_string('mpirun -np 2 namd2 +p4 test.conf')
        self.assertEqual(result, 'NAMD')

    def test_check_command_line_split_gromacs_basic(self):
        preamble, executable, arguments = utilities.command_line_split('mpirun gmx mdrun -deffnm test')
        self.assertTupleEqual((preamble, executable, arguments),(['mpirun'], ['gmx','mdrun'], ['-deffnm', 'test']))

    def test_check_command_line_split_amber_basic(self):
        preamble, executable, arguments = utilities.command_line_split('sander -O -i test.in')
        self.assertTupleEqual((preamble, executable, arguments),([], ['sander'], ['-O', '-i', 'test.in']))

    def test_check_command_line_split_namd_basic(self):
        preamble, executable, arguments = utilities.command_line_split('namd2 test.conf')
        self.assertTupleEqual((preamble, executable, arguments),([], ['namd2'], ['test.conf']))

    def test_check_command_line_split_namd_advanced(self):
        preamble, executable, arguments = utilities.command_line_split('aprun -n 2 namd2 +p8 test.conf')
        self.assertTupleEqual((preamble, executable, arguments),(['aprun', '-n', '2'], ['namd2'], ['+p8', 'test.conf']))

    def test_check_string_to_inputs_dict_gromacs_basic(self):
        inputs = utilities.string_to_inputs_dict('mpirun gmx mdrun -deffnm test -imdwait')
        expected_inputs = {-1 : ['mpirun'], 0 : ['gmx', 'mdrun'],
                           '-s' : 'test.tpr', 
                           '-g' : 'test.log', 
                           '-e' : 'test.edr', 
                           '-o' : 'test.trr', 
                           '-x' : 'test.xtc', 
                           '-cpo' : 'test.cpt', 
                           '-imdwait' : None}
        self.assertDictEqual(expected_inputs, inputs)

    def test_check_string_to_inputs_dict_amber_basic(self):
        inputs = utilities.string_to_inputs_dict('pmemd -O -i test.in -o test.out')
        expected_inputs = {-1 : [], 0 : ['pmemd'], '-O' : None, '-i' : 'test.in', '-o' : 'test.out'}
        self.assertDictEqual(expected_inputs, inputs)

    def test_check_string_to_inputs_dict_namd_basic(self):
        inputs = utilities.string_to_inputs_dict('namd2 +p4 test.conf')
        expected_inputs = {-1 : [], 0 : ['namd2'], 1 : '+p4', 2 : 'test.conf'}
        self.assertDictEqual(expected_inputs, inputs)
    '''
    def test_inputs_dict_to_string_gromacs(self):
        expected_command = 'mpirun gmx mdrun -deffnm test -imdwait'
        inputs = utilities.string_to_inputs_dict(expected_command)
        command = utilities.inputs_dict_to_string(inputs)
        self.assertEqual(expected_command, command)
    '''

    def test_inputs_dict_to_string_amber(self):
        expected_command = 'pmemd.MPI -O -i test.in -o test.out'
        inputs = utilities.string_to_inputs_dict(expected_command)
        command = utilities.inputs_dict_to_string(inputs)
        options = ['pmemd.MPI -O -i test.in -o test.out',
                   'pmemd.MPI -O -o test.out -i test.in',
                   'pmemd.MPI -i test.in -O -o test.out',
                   'pmemd.MPI -i test.in -o test.out -O',
                   'pmemd.MPI -o test.out -O -i test.in',
                   'pmemd.MPI -o test.out -i test.in -O']
        self.assertTrue(command in options)

    def test_inputs_dict_to_string_namd(self):
        expected_command = 'namd2 +p4 test.conf' 
        inputs = utilities.string_to_inputs_dict(expected_command)
        command = utilities.inputs_dict_to_string(inputs)
        self.assertEqual(command, expected_command)

    def test_inputs_dict_to_filepack_gromacs(self):
        command = 'gmx mdrun -s test/examples/bpti.tpr -imdwait'
        inputs = utilities.string_to_inputs_dict(command)
        filepack = utilities.inputs_dict_to_filepack(inputs)
        self.assertIsInstance(filepack, dict)

    def test_filepack_to_inputs_dict(self):
        command = 'gmx mdrun -s test/examples/bpti.tpr -imdwait'
        inputs = utilities.string_to_inputs_dict(command)
        filepack = utilities.inputs_dict_to_filepack(inputs)
        new_inputs = utilities.filepack_to_inputs_dict(filepack, targetdir=self.testdir)
        self.assertEqual(new_inputs['-s'], '{}/bpti.tpr'.format(self.testdir))
        self.assertTrue(os.path.exists(new_inputs['-s']))

