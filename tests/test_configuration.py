from pathlib import Path
import sys
from typing import Literal
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
        settings.load_file(temp_config_file, validate=True)

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
        settings.load_file(temp_config_file, validate=True)

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
        settings.load_file(temp_config_file, validate=True)

        try:
            settings["features"]["shipping"]["default_interval"]
        except KeyError as e:
            self.fail(f"Parsed configuration does not have key 'features.shipping.default_interval' (error: {e})")

        self.assertEqual(
            settings["features"]["shipping"]["default_interval"],
            '07:00-16:00'
        )

class ConfigurationValuesTestCase(unittest.TestCase):
    maxDiff = None

    def assertHasKey(self, obj, key, access_method: Literal["dict", "getattr"]="dict") -> None:
        """ Assert that the given object has the given key. """
        current_obj = obj
        for k in key.split("."):
            try:
                if access_method == "dict":
                    current_obj = current_obj[k]
                elif access_method == "getattr":
                    current_obj = getattr(current_obj, k)
            except KeyError:
                self.fail(f"Object '{current_obj}' does not have key '{k}'")

    @with_temporary_file(file_prefix="veryeasyfatt-", file_suffix=".toml", content="""
        [easyfatt.customers]
        export_filename = ["file.xlsx"]
    """)
    def test_single_list(self, temp_config_file: Path):
        settings = _get_settings()
        settings.load_file(temp_config_file, validate=True)

        self.assertHasKey(settings, "easyfatt.customers.export_filename")
        
        # See issue [#999](https://github.com/dynaconf/dynaconf/issues/999)
        self.assertIn(
            Path("file.xlsx"),
            settings.easyfatt.customers.export_filename
        )
        # FIXME: This assertion fails because the value gets merged with the default value
        # self.assertEqual(
        #     settings.easyfatt.customers.export_filename,
        #     [Path("file.xlsx")],
        # )

    @with_temporary_file(file_prefix="veryeasyfatt-", file_suffix=".toml", content="""
        [easyfatt.customers]
        export_filename = "file.xlsx"
    """)
    def test_single_string(self, temp_config_file: Path):
        settings = _get_settings()
        settings.load_file(temp_config_file, validate=True)

        self.assertHasKey(settings, "easyfatt.customers.export_filename")
        
        self.assertEqual(
            settings.easyfatt.customers.export_filename,
            [Path("file.xlsx")],
        )

    @with_temporary_file(file_prefix="veryeasyfatt-", file_suffix=".toml", content="""
        [easyfatt.customers]
    """)
    def test_empty_value(self, temp_config_file: Path):
        settings = _get_settings()
        settings.load_file(temp_config_file, validate=True)

        self.assertHasKey(settings, "easyfatt.customers.export_filename")
        
        self.assertEqual(
            settings.easyfatt.customers.export_filename,
            [ Path("Soggetti.xlsx"), Path("Soggetti.ods") ],
        )


if __name__ == '__main__':
    unittest.main(verbosity=2)