from chibi.command import command
from unittest import TestCase


class Test_command( TestCase ):
    def test_should_return_a_tuple_of_3_elements( self ):
        result = command( 'echo', 'SAMPLE_TEXT', stdout='pipe' )
        self.assertIsInstance( result, tuple )
        self.assertEqual( len( result ), 3 )

    def test_if_send_pipe_in_stdout_should_return_the_stdout( self ):
        out, error, return_code = command(
            'echo', 'SAMPLE_TEXT', stdout='pipe' )
        self.assertEqual( out, 'SAMPLE_TEXT\n' )

    def test_if_send_pipe_in_stderr_should_return_the_stderr( self ):
        out, error, return_code = command(
            'cp', 'FILE_NOT_FOUND', 'TO_ANOTHER_IMPOSIBLE_PLACE',
            stderr='pipe' )
        self.assertTrue( error )


class Test_command_error( TestCase ):
    def test_the_return_code_should_be_different_to_0( self ):
        out, error, return_code = command(
            'cp', 'FILE_NOT_FOUND', 'TO_ANOTHER_IMPOSIBLE_PLACE',
            stderr='pipe' )
        self.assertNotEqual( return_code, 0 )


class Test_command_success( TestCase ):
    def test_the_return_code_should_be_equal_to_0( self ):
        out, error, return_code = command(
            'echo', 'SAMPLE_TEXT', stdout='pipe' )
        self.assertEqual( return_code, 0 )
