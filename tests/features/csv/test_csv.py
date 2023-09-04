from pathlib import Path
import subprocess
import sys
import unittest

from veryeasyfatt.app.config_manager import get_configuration

# Hack needed to include scripts from the `scripts` directory (under root)
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from tests.utils.decorators import with_temporary_file


class ConfigurationTestCase(unittest.TestCase):
    _executable_name = Path("./src/veryeasyfatt/bootstrap.py").resolve()

    @with_temporary_file(file_prefix="veryeasyfatt-", file_suffix=".toml", content="""
        [files.input]
        easyfatt = "./tests/features/csv/Documents.DefXml"
    """)
    @with_temporary_file(file_prefix="veryeasyfatt2-", file_suffix=".toml", content="""
        [files.input]
        easyfatt = "./tests/features/csv/Documents.DefXml"
    """)
    def test_changed_value(self, configuration_file: Path, configuration_file2: Path):
        print(configuration_file, configuration_file2)
        command_output = subprocess.run(
            [
                sys.executable,
                self._executable_name,
                "--disable-version-check",
                "--disable-rich-logging",
                "-c",
                configuration_file,
                "--goal",
                "csv-generator",
            ],
            timeout=360,
            input="\nn\nn\n",
            capture_output=True,
            text=True,
        ).stdout

        self.assertRegex(command_output, r"Creazione CSV '\./Documenti\.csv' terminata")



if __name__ == '__main__':
    unittest.main(verbosity=2)