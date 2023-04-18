import os
import subprocess
import tempfile
from rich.logging import RichHandler
import logging

from pathlib import Path

import pyinstaller_versionfile
import updater

logger = logging.getLogger(__name__)

def main():
	logger.addHandler(RichHandler(
		rich_tracebacks=True,
		omit_repeated_times=False,
		log_time_format="[%d-%m-%Y %H:%M:%S]"
	))
	logger.setLevel(logging.INFO)

	build("./src/bootstrap.py", "easyfatt_integration")

def quote(string, quote='"'):
	return quote + string + quote

def build(filename: str, output_name: str|None = None, clean=True):
	original_filename: str = f"{Path(output_name).name}.exe" if output_name else f"{Path(filename).stem}.exe"

	(fd, temporary_version_file) = tempfile.mkstemp(prefix="versionFile-", suffix=".txt", text=True)
	os.close(fd)

	try:
		pyinstaller_versionfile.create_versionfile(
			output_file=temporary_version_file,
			version=updater.get_current_version(),

			company_name="Luca Salvarani",
			file_description="Automazione flussi aziendali Easyfatt",
			internal_name=Path(original_filename).stem,
			original_filename=Path(original_filename).name,
			product_name="VeryEasyfatt Extra tools",

			# Language (Italian) & Charset (Multilingual)
			translations=[1252, 1040]
		)

		logger.info("Starting build")
		build_command = [
			'pyinstaller',
			'--log-level', 'ERROR',
			'--noconfirm',
			'--onefile', 
			# '--add-data', r'./src/;./src/',
			'--add-data', r'./pyproject.toml;.',
			'--add-data', r'./veryeasyfatt.config.toml;.',
			'--version-file', temporary_version_file,
			# '--path', r'./src/',
		]

		if clean:
			logger.debug(f"The build will run in 'clean' mode")
			build_command.extend(['--clean'])
		
		if output_name:
			logger.debug(f"A custom name was provided: '{output_name}'")
			build_command.extend(['--name', str(output_name)])
		
		build_command.append(str(filename))

		logger.info(f"Sending command: '{' '.join(map(quote, build_command))}'")
		build_process = subprocess.run(
			build_command, 
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
		)
	except Exception:
		raise
	finally:
		Path(temporary_version_file).unlink()

	if build_process.returncode != 0:
		print(build_process.stderr)
		logger.error("Build failed")
		return False

	logger.debug(f"STDOUT: '{build_process.stdout}'")
	logger.debug(f"STDERR: '{build_process.stderr}'")
	logger.info("Build ended")
	return True

if __name__ == '__main__':
	main()