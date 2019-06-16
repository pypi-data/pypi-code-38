import unittest

from rabbitholer.main import get_arg_parser


class Arguments(unittest.TestCase):

    commands = ['send', 'read', 'monitor', 'pipe']

    def test_read(self):
        parser = get_arg_parser()
        args = ['read']
        parsed = parser.parse_args(args)
        self.assertEqual(parsed.command, 'read')

    def test_pipe(self):
        parser = get_arg_parser()
        args = ['pipe', './hole1']
        parsed = parser.parse_args(args)
        self.assertEqual(parsed.command, 'pipe')
        self.assertEqual(parsed.pipe_name, './hole1')

    def test_monitor(self):
        parser = get_arg_parser()
        args = ['monitor']
        parsed = parser.parse_args(args)
        self.assertEqual(parsed.command, 'monitor')

    def test_send(self):
        parser = get_arg_parser()
        args = ['send', 'msg1', 'msg2']
        parsed = parser.parse_args(args)
        self.assertEqual(parsed.command, 'send')
        self.assertEqual(parsed.messages, ['msg1', 'msg2'])

    def test_server(self):
        parser = get_arg_parser()

        for com in self.commands:
            args = [com] + ['-s', 'serv1']
            parsed = parser.parse_args(args)
            self.assertEqual(parsed.server, 'serv1')

            args = [com] + ['--server', 'serv1']
            parsed = parser.parse_args(args)
            self.assertEqual(parsed.server, 'serv1')

    def test_routing(self):
        parser = get_arg_parser()

        for com in self.commands:
            args = [com] + ['-r', 'ro1']
            parsed = parser.parse_args(args)
            self.assertEqual(parsed.routing_key, 'ro1')

            args = [com] + ['--routing', 'ro1']
            parsed = parser.parse_args(args)
            self.assertEqual(parsed.routing_key, 'ro1')

    def test_queue(self):
        parser = get_arg_parser()

        for com in self.commands:
            args = [com] + ['-q', 'qu1']
            parsed = parser.parse_args(args)
            self.assertEqual(parsed.queue, 'qu1')

            args = [com] + ['--queue', 'qu1']
            parsed = parser.parse_args(args)
            self.assertEqual(parsed.queue, 'qu1')

    def test_exchange(self):
        parser = get_arg_parser()

        for com in self.commands:
            args = [com] + ['-e', 'exch1']
            parsed = parser.parse_args(args)
            self.assertEqual(parsed.exchange, 'exch1')

            args = [com] + ['--exchange', 'exch1']
            parsed = parser.parse_args(args)
            self.assertEqual(parsed.exchange, 'exch1')

    def test_very_verbose(self):
        parser = get_arg_parser()

        args = ['-vvv']
        parsed = parser.parse_args(args)
        self.assertTrue(parsed.very_verbose)

        args = ['--very-verbose']
        parsed = parser.parse_args(args)
        self.assertTrue(parsed.very_verbose)

    def test_verbose(self):
        parser = get_arg_parser()

        args = ['-vv']
        parsed = parser.parse_args(args)
        self.assertTrue(parsed.verbose)

        args = ['--verbose']
        parsed = parser.parse_args(args)
        self.assertTrue(parsed.verbose)

    def test_version(self):
        parser = get_arg_parser()
        with self.assertRaises(SystemExit):
            args = ['-v']
            parser.parse_args(args)
        with self.assertRaises(SystemExit):
            args = ['--version']
            parser.parse_args(args)

    def test_help(self):
        parser = get_arg_parser()
        with self.assertRaises(SystemExit):
            args = ['-h']
            parser.parse_args(args)
        with self.assertRaises(SystemExit):
            args = ['--help']
            parser.parse_args(args)


if __name__ == '__main__':
    unittest.main()
