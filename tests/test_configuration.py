import functools
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest

import textwrap
from config_manager import get_configuration

# Hack needed to include scripts from the `scripts` directory (under root)
sys.path.append(str(Path(__file__).resolve().parent.parent))
import scripts.build as builder_script
from tests.utils.decorators import with_temporary_file


class ConfigurationTestCase(unittest.TestCase):
    @with_temporary_file()
    def test_configuration(self, temp_config_file: Path):
        temp_config_file.write_text(textwrap.dedent("""
            log_level = "WARNING"

            [files.input]
            easyfatt = "./EasyfattTesting.DefXml"
            addition = ""

            [features.shipping]
            default_interval = "00:00-06:00"
        """))

        parsed_configuration = get_configuration(temp_config_file)
        expect_configuration = {
            'log_level': 'WARNING', 
            'easyfatt': {
                'customers': {
                    'custom_field': 1, 
                    'export_filename': ['Soggetti.xlsx', 'Soggetti.ods']
                }
            }, 
            'files': {
                'input': {
                    'easyfatt': './EasyfattTesting.DefXml', 
                    'addition': ''
                }, 
                'output': {
                    'csv': './Documenti.csv'
                }
            }, 
            'options': {
                'output': {
                    'csv_template': '@{CustomerName} {CustomerCode}@{eval_IndirizzoSpedizione} {eval_CAPSpedizione} {eval_CittaSpedizione}(20){eval_intervalloSpedizione}^{eval_pesoSpedizione}^'
                }
            }, 
            'features': {
                'shipping': {
                    'default_interval': '00:00-06:00'
                }
            }
        }
        self.assertEqual(
            parsed_configuration,
            expect_configuration
        )
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


if __name__ == '__main__':
    unittest.main(verbosity=2)