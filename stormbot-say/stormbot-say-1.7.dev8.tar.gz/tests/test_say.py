from unittest import TestCase, mock
import asyncio

from stormbot_say import Say

def _run(coro):
    asyncio.get_event_loop().run_until_complete(coro)

class TestSayCommand(TestCase):
    def test_argparser(self):
        # Given
        mock_arg_parse = mock.Mock()

        # When
        Say.argparser(mock_arg_parse)

        # Then
        mock_arg_parse.add_argument.assert_called()

    def test_cmdparser(self):
        # Given
        mock_bot = mock.Mock()
        mock_args = mock.Mock()
        mock_arg_parse = mock.Mock()
        plugin = Say(mock_bot, mock_args)

        # When
        plugin.cmdparser(mock_arg_parse)

        # Then
        mock_arg_parse.add_parser.assert_called()

    @mock.patch('stormbot_say.subprocess')
    @mock.patch('stormbot_say.gTTS')
    def test_normal_run(self, mock_tts, mock_subprocess):
        # Given
        mock_bot = mock.Mock()
        mock_bot.get_peers.return_value = [mock.Mock(), mock.Mock()]
        mock_args = mock.Mock()

        mock_parser = mock.Mock()
        mock_parsed_args = mock.Mock()
        plugin = Say(mock_bot, mock_args)
        raw_msg = "hello"

        # When
        _run(plugin.run(raw_msg, mock_parser, mock_parsed_args, None))

        # Then
        for mock_peer in mock_bot.get_peers.return_value:
            mock_bot.peer_forward_msg.assert_any_call(plugin, mock_peer, raw_msg)

        mock_tts.assert_called_with(lang=mock_parsed_args.lang, text=mock_parsed_args.text)
        mock_tts.return_value.write_to_fp.assert_called()
        mock_subprocess.check_call.assert_called()
        mock_bot.write.assert_called_with(mock_parsed_args.text)

    @mock.patch('stormbot_say.subprocess')
    @mock.patch('stormbot_say.gTTS')
    def test_run_from_peer(self, mock_tts, mock_subprocess):
        # Given
        mock_bot = mock.Mock()
        mock_bot.get_peers.return_value = [mock.Mock(), mock.Mock()]
        mock_args = mock.Mock()

        mock_parser = mock.Mock()
        mock_parsed_args = mock.Mock()
        plugin = Say(mock_bot, mock_args)
        raw_msg = "hello"

        # When
        _run(plugin.run(raw_msg, mock_parser, mock_parsed_args, "peer_id"))

        # Then
        mock_bot.peer_forward_msg.assert_not_called()

        mock_tts.assert_called_with(lang=mock_parsed_args.lang, text=mock_parsed_args.text)
        mock_tts.return_value.write_to_fp.assert_called()
        mock_subprocess.check_call.assert_called()
        mock_bot.write.assert_not_called()
