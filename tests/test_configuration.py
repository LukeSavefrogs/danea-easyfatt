from pathlib import Path
import sys
import unittest

from app.config_manager import get_configuration

# Hack needed to include scripts from the `scripts` directory (under root)
sys.path.append(str(Path(__file__).resolve().parent.parent))
from tests.utils.decorators import with_temporary_file


class ConfigurationTestCase(unittest.TestCase):
    @with_temporary_file(file_prefix="veryeasyfatt-", file_suffix=".toml", content="""
        [features.shipping]
        default_interval = "00:00-06:00"
    """)
    def test_changed_value(self, temp_config_file: Path):
        parsed_configuration = get_configuration(temp_config_file)
        
        self.assertEqual(
            parsed_configuration,
            parsed_configuration | {
                'features': {
                    'shipping': {
                        'default_interval': '00:00-06:00'
                    }
                }
            }
        )

    @with_temporary_file(file_prefix="veryeasyfatt-", file_suffix=".toml", content="""
        [features.shipping]
        default_interval = ""
    """)
    def test_empty_value(self, temp_config_file: Path):
        parsed_configuration = get_configuration(temp_config_file)
        
        self.assertEqual(
            parsed_configuration,
            parsed_configuration | {
                'features': {
                    'shipping': {
                        'default_interval': ''
                    }
                }
            }
        )

    @with_temporary_file(file_prefix="veryeasyfatt-", file_suffix=".toml", content="""
        [features.shipping]
    """)
    def test_default_value(self, temp_config_file: Path):
        parsed_configuration = get_configuration(temp_config_file)
        
        self.assertEqual(
            parsed_configuration,
            parsed_configuration | {
                'features': {
                    'shipping': {
                        'default_interval': '07:00-16:00'
                    }
                }
            }
        )

    # @with_temporary_file(file_prefix="veryeasyfatt-", file_suffix=".toml", content="""
    #     [features.shipping.default_interval]
    #     test = ""
    # """)
    # def test_err_value(self, temp_config_file: Path):
    #     with self.assertRaises(Exception):
    #         get_configuration(temp_config_file)


if __name__ == '__main__':
    unittest.main(verbosity=2)