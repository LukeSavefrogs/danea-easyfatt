import subprocess
from rich.logging import RichHandler
import logging

from pathlib import Path
import git


logger = logging.getLogger(__name__)
logger.addHandler(RichHandler(
	rich_tracebacks=True,
	omit_repeated_times=False,
	log_time_format="[%d-%m-%Y %H:%M:%S]"
))
logger.setLevel(logging.INFO)

def main():
	build("./src/main.py", "easyfatt_integration")
	# build("./src/test.py", "TEST")

def quote(string, quote='"'):
	return quote + string + quote

def build(filename, output_name = None, clean=True):
	logger.info("Starting build")
	build_command = [
		'pyinstaller',
		'--log-level', 'ERROR',
		'--noconfirm',
		'--onefile', 
		'--add-data', r'./src/;./src/',
		'--add-data', r'./pyproject.toml;.',
		'--add-data', r'./veryeasyfatt.config.toml;.',
		'--path', r'./src/',
	]

	if clean:
		logger.debug(f"The build will run in 'clean' mode")
		build_command.extend(['--clean'])
	
	if output_name:
		logger.debug(f"A custom name was provided: '{output_name}'")
		build_command.extend(['--name', output_name])
	
	build_command.append(filename)

	logger.info(f"Sending command: '{' '.join(map(quote, build_command))}'")
	build_process = subprocess.run(
		build_command, 
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
	)

	if build_process.returncode != 0:
		logger.error("Build failed")
		return False

	logger.debug(f"STDOUT: '{build_process.stdout}'")
	logger.debug(f"STDERR: '{build_process.stderr}'")
	logger.info("Build ended")
	return True

if __name__ == '__main__':
	main()