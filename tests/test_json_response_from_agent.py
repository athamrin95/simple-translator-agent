import unittest
from unittest.mock import MagicMock
from openai import OpenAI

from translator_agent import parse_json, call_ai, INSTRUCTIONS

class TestTranslatorAgent(unittest.TestCase):

    def test_parse_json_clean(self):
        raw_text = '{"en": "Hello", "ja": "こんにちは"}'
        result = parse_json(raw_text)
        self.assertEqual(result, {"en": "Hello", "ja": "こんにちは"})

    def test_parse_json_with_markdown_fences(self):
        raw_text = '```json\n{"en": "Good morning", "ja": "おはようございます"}\n```'
        result = parse_json(raw_text)
        self.assertEqual(result, {"en": "Good morning", "ja": "おはようございます"})

    def test_call_ai_success(self):
        mock_client = MagicMock(spec=OpenAI)
        mock_response = MagicMock()
        mock_response.output_text = '{"en": "Thank you", "ja": "ありがとう"}'
        mock_client.responses.create.return_value = mock_response

        call_ai(mock_client, "Terima kasih", "test-model")
        mock_client.responses.create.assert_called_once_with(
            model="test-model",
            instructions=INSTRUCTIONS,
            input="Terima kasih"
        )

    def test_call_ai_retry_on_json_decode_error(self):
        mock_client = MagicMock(spec=OpenAI)
        bad_response = MagicMock()
        bad_response.output_text = 'not a valid json'
        good_response = MagicMock()
        good_response.output_text = '{"en": "Yes", "ja": "はい"}'
        mock_client.responses.create.side_effect = [bad_response, good_response]

        call_ai(mock_client, "Ya", "test-model")
        self.assertEqual(mock_client.responses.create.call_count, 2)

    def test_call_ai_retry_on_missing_key(self):
        mock_client = MagicMock(spec=OpenAI)
        bad_response = MagicMock()
        bad_response.output_text = '{"en": "No"}'
        good_response = MagicMock()
        good_response.output_text = '{"en": "No", "ja": "いいえ"}'
        mock_client.responses.create.side_effect = [bad_response, good_response]

        call_ai(mock_client, "Tidak", "test-model")
        self.assertEqual(mock_client.responses.create.call_count, 2)

if __name__ == "__main__":
    unittest.main()