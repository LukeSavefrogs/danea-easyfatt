from pathlib import Path
import secrets
import subprocess
import sys
import unittest
import shutil

from packaging.version import Version

# Hack needed to include scripts from the `scripts` directory (under root)
sys.path.append(str(Path(__file__).resolve().parent.parent))

from tests.utils.decorators import with_temporary_file
import scripts.build as builder_script


class BundleTestCase(unittest.TestCase):
    """Tests for the bundled executable"""

    _executable_name: Path
    _python_scr_name: Path

    @classmethod
    def setUpClass(cls):
        cls._executable_name = Path(f"./dist/{secrets.token_hex(16)}.exe")
        cls._python_scr_name = Path("./src/veryeasyfatt/bootstrap.py").resolve()

        # 1. Build the temporary executable file
        if not builder_script.build(
            str(cls._python_scr_name), cls._executable_name.stem
        ):
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
            [self._executable_name, "-h"],
            timeout=360,
            input="\n",
            capture_output=True,
            check=True,
            text=True,
        ).stdout

        self.assertRegex(command_output, r"usage:.*")

    def test_version(self):
        command_output = subprocess.run(
            [self._executable_name, "--version"],
            timeout=360,
            input="\n",
            capture_output=True,
            check=True,
            text=True,
        ).stdout

        self.assertRegex(command_output, r"v[0-9]+\.[0-9]+\.[0-9]+.*")

    def test_no_version_check(self):
        """Tests if no version check is done."""
        command_output = subprocess.run(
            [
                self._executable_name,
                "--disable-rich-logging",
                "--disable-version-check",
                "--goal",
                "csv-generator",
            ],
            timeout=360,
            input="\nn\nn\n",
            capture_output=True,
            text=True,
        ).stdout

        self.assertRegex(
            command_output, "Il controllo versione è stato disattivato tramite CLI"
        )

    @with_temporary_file(
        file_prefix="veryeasyfatt-",
        file_suffix=".toml",
        content=f"""
        [files.input]
        easyfatt = "./{secrets.token_hex(32)}.DefXml"
    """,
    )
    def test_error_file_not_found(self, configuration_file: Path):
        """Tests the behaviour of the program when a required file is not present"""
        command_output = subprocess.run(
            [
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

        self.assertRegex(command_output, r"File richiesto '.*\.DefXml' non trovato\.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
