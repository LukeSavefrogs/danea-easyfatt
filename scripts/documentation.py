import subprocess
from rich.logging import RichHandler
import logging

from pathlib import Path


logger = logging.getLogger(__name__)
logger.addHandler(RichHandler(
	rich_tracebacks=True,
	omit_repeated_times=False,
	log_time_format="[%d-%m-%Y %H:%M:%S]"
))
logger.setLevel(logging.INFO)

def install_deps():
	logger.info("Dependency installation started")

	build_process = subprocess.run(
		[ 'bundle', 'install' ],
		capture_output=True,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
	)

	if build_process.returncode != 0:
		logger.error("Dependency installation failed")
		logger.debug(f"STDOUT: '{build_process.stdout}'")
		logger.debug(f"STDERR: '{build_process.stderr}'")
		return False

	logger.info("Dependency installation ended")


def serve():
	logger.info("Website generation started")

	build_process = subprocess.run(
		[ 'bundle', 'exec', 'jekyll', 'serve', '--incremental' ], 
		capture_output=True,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
	)

	if build_process.returncode != 0:
		logger.error("Website generation failed")
		logger.debug(f"STDOUT: '{build_process.stdout}'")
		logger.debug(f"STDERR: '{build_process.stderr}'")
		return False

	logger.info("Website generation ended")



def main():
	if not install_deps():
		return False

	if not serve():
		return False


if __name__ == '__main__':
	main()