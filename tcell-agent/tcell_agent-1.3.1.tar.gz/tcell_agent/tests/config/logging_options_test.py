import unittest

from tcell_agent.config.logging_options import LoggingOptions


class LoggingOptionsTest(unittest.TestCase):
    def test_none_dict(self):
        logging_options = LoggingOptions()

        self.assertEqual(logging_options["enabled"], True)
        self.assertEqual(logging_options["level"], "INFO")
        self.assertEqual(logging_options["filename"], "tcell_agent.log")

    def test_empty_dict(self):
        logging_options = LoggingOptions({})

        self.assertEqual(logging_options["enabled"], True)
        self.assertEqual(logging_options["level"], "INFO")
        self.assertEqual(logging_options["filename"], "tcell_agent.log")

    def test_enabled_values(self):
        logging_options = LoggingOptions({"enabled": False})
        self.assertEqual(logging_options["enabled"], False)

        logging_options = LoggingOptions({"enabled": True})
        self.assertEqual(logging_options["enabled"], True)

        logging_options = LoggingOptions({"enabled": "string"})
        self.assertEqual(logging_options["enabled"], False)

        logging_options = LoggingOptions({"enabled": None})
        self.assertEqual(logging_options["enabled"], True)

        logging_options = LoggingOptions({"enabled": ""})
        self.assertEqual(logging_options["enabled"], False)

        logging_options = LoggingOptions({"enabled": 1245})
        self.assertEqual(logging_options["enabled"], False)

    def test_level_values(self):
        logging_options = LoggingOptions({"level": None})
        self.assertEqual(logging_options["level"], "INFO")

        logging_options = LoggingOptions({"level": ""})
        self.assertEqual(logging_options["level"], "INFO")

        logging_options = LoggingOptions({"level": "UNKNOWN"})
        self.assertEqual(logging_options["level"], "INFO")

        logging_options = LoggingOptions({"level": True})
        self.assertEqual(logging_options["level"], "INFO")

        logging_options = LoggingOptions({"level": 12355})
        self.assertEqual(logging_options["level"], "INFO")

        logging_options = LoggingOptions({"level": "DEBUG"})
        self.assertEqual(logging_options["level"], "DEBUG")

    def test_filename_values(self):
        logging_options = LoggingOptions({"filename": None})
        self.assertEqual(logging_options["filename"], "tcell_agent.log")

        logging_options = LoggingOptions({"filename": ""})
        self.assertEqual(logging_options["filename"], "tcell_agent.log")

        logging_options = LoggingOptions({"filename": True})
        self.assertEqual(logging_options["filename"], "True")

        logging_options = LoggingOptions({"filename": 12355})
        self.assertEqual(logging_options["filename"], "12355")

        logging_options = LoggingOptions({"filename": "custom.log"})
        self.assertEqual(logging_options["filename"], "custom.log")

    def test_happy_path(self):
        logging_options = LoggingOptions({
            "enabled": False,
            "level": "DEBUG",
            "filename": "custom.log"
        })

        self.assertEqual(logging_options["enabled"], False)
        self.assertEqual(logging_options["level"], "DEBUG")
        self.assertEqual(logging_options["filename"], "custom.log")
