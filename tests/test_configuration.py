from pathlib import Path
import sys
import unittest

from veryeasyfatt.configuration import _get_settings

# Hack needed to include scripts from the `scripts` directory (under root)
sys.path.append(str(Path(__file__).resolve().parent.parent))
from tests.utils.decorators import with_temporary_file


class ConfigurationTestCase(unittest.TestCase):
    maxDiff = None

    @with_temporary_file(file_prefix="veryeasyfatt-", file_suffix=".toml", content="""
        [features.shipping]
        default_interval = "00:00-06:00"
    """)
    def test_changed_value(self, temp_config_file: Path):
        settings = _get_settings()
        settings.load_file(temp_config_file)

        try:
            settings["features"]["shipping"]["default_interval"]
        except KeyError as e:
            self.fail(f"Parsed configuration does not have key 'features.shipping.default_interval' (error: {e})")

        self.assertEqual(
            settings["features"]["shipping"]["default_interval"],
            '00:00-06:00'
        )

    @with_temporary_file(file_prefix="veryeasyfatt-", file_suffix=".toml", content="""
        [features.shipping]
        default_interval = ""
    """)
    def test_empty_value(self, temp_config_file: Path):
        settings = _get_settings()
        settings.load_file(temp_config_file)

        try:
            settings["features"]["shipping"]["default_interval"]
        except KeyError as e:
            self.fail(f"Parsed configuration does not have key 'features.shipping.default_interval' (error: {e})")

        self.assertEqual(
            settings["features"]["shipping"]["default_interval"],
            ''
        )

    @with_temporary_file(file_prefix="veryeasyfatt-", file_suffix=".toml", content="""
        [features.shipping]
    """)
    def test_default_value(self, temp_config_file: Path):
        settings = _get_settings()
        settings.load_file(temp_config_file)

        try:
            settings["features"]["shipping"]["default_interval"]
        except KeyError as e:
            self.fail(f"Parsed configuration does not have key 'features.shipping.default_interval' (error: {e})")

        self.assertEqual(
            settings["features"]["shipping"]["default_interval"],
            '07:00-16:00'
        )


if __name__ == '__main__':
    unittest.main(verbosity=2)