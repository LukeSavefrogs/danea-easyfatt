from pathlib import Path
import secrets
import subprocess
import sys
import unittest
import shutil

from packaging.version import Version

# Hack needed to include scripts from the `scripts` directory (under root)
sys.path.append(str(Path(__file__).resolve().parent.parent))

import scripts.build as builder_script

class BundleTestCase(unittest.TestCase):
    _executable_name: Path
    _python_scr_name: Path

    @classmethod
    def setUpClass(cls):
        cls._executable_name = Path(f"./dist/{secrets.token_hex(16)}.exe")
        cls._python_scr_name = Path("./src/main.py").resolve()

        # 1. Build the temporary executable file
        if not builder_script.build(cls._python_scr_name, cls._executable_name.stem):
            raise Exception("Failed creating executable.")
        
        # 2. Remove the temporary build spec file
        for file in Path("./").glob(cls._executable_name.stem + ".spec"):
            file.unlink()

        # 3. Remove the temporary build directory
        for directory in Path("./build").glob(cls._executable_name.stem):
            shutil.rmtree(directory)

    @classmethod
    def tearDownClass(cls):
        # Remove the temporary executable file
        cls._executable_name.unlink()



    def test_help(self):
        command_output = subprocess.run(
            [self._executable_name, '-h'], timeout=360,
            input='\n', capture_output=True, check=True, text=True,
        ).stdout

        self.assertRegex(command_output, r"usage:.*")

    def test_version(self):
        command_output = subprocess.run(
            [self._executable_name, '--version'], timeout=360,
            input='\n', capture_output=True, check=True, text=True,
        ).stdout

        self.assertRegex(command_output, r"v[0-9]+\.[0-9]+\.[0-9]+.*")


if __name__ == '__main__':
    unittest.main(verbosity=2)