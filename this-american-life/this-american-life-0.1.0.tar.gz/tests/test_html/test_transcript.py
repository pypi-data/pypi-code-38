
import unittest
from unittest.mock import patch, MagicMock
from thisamericanlife.html.transcript import TranscriptHtml


class TestHtmlTranscriptParsing(unittest.TestCase):
    @patch('thisamericanlife.html.transcript.lxml_html')
    def get_mocked_transcript_html(self, mock_lxml_html, html_string=None):
        t = TranscriptHtml(html_string=html_string)
        mock_lxml_html.fromstring.assert_called_once_with(html_string)
        return t

    def test_initialized_with_parsed_html(self):
        self.get_mocked_transcript_html()

    @patch('thisamericanlife.html.transcript.TranscriptHtml.extract_transcript')
    @patch('thisamericanlife.html.transcript.TranscriptHtml.extract_episode_title')
    def test_to_json(self, mock_extract_transcript, mock_extract_episode_title, *args):

        res = self.get_mocked_transcript_html().to_json()
        mock_extract_transcript.assert_called_once()
        mock_extract_episode_title.assert_called_once()

        expected_result = dict(episode_title=mock_extract_transcript(), transcript=mock_extract_episode_title())
        self.assertDictEqual(res, expected_result)

    @patch('thisamericanlife.html.transcript.get_header_text')
    def test_extract_episode_title(self, mock_get_header_text, *args):
        t = self.get_mocked_transcript_html()
        res = t.extract_episode_title()

        t.document_tree.xpath.assert_called_once_with(TranscriptHtml.EPISODE_TITLE_PATH)
        mock_get_header_text.assert_called_once_with(t.document_tree.xpath().__getitem__(0))
        self.assertEqual(res, mock_get_header_text())


if __name__ == '__main__':
    unittest.main()
