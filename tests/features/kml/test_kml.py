from pathlib import Path
import subprocess
import sys
import unittest

# Hack needed to include scripts from the `scripts` directory (under root)
sys.path.append(str(Path(__file__).resolve().parent.parent))
from tests.utils.decorators import with_temporary_file


class KMLGenerationTestCase(unittest.TestCase):
    maxDiff = None
    _executable_name = Path("./src/veryeasyfatt/bootstrap.py").resolve()

    @with_temporary_file(file_prefix="veryeasyfatt-", file_suffix=".toml", content="""
        [files.input]
        easyfatt = "./tests/features/kml/Documents.DefXml"

        [features.kml_generation]
        google_api_key = ""
    """)
    def test_empty_api_key(self, configuration_file: Path):
        command_output = subprocess.run(
            [
                sys.executable,
                self._executable_name,
                "--disable-version-check",
                "--disable-rich-logging",
                "-c",
                configuration_file,
                "--goal",
                "kml-generator",
            ],
            timeout=360,
            input="\nn\nn\n",
            capture_output=True,
            text=True,
        ).stdout

        self.assertRegex(command_output, r"Google API key not found in the configuration file")



if __name__ == '__main__':
    unittest.main(verbosity=2)