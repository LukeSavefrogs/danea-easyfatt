import logging
from pathlib import Path
import sys

import requests
import json

import toml
from packaging.version import Version

import bundle.path as bundle

REPO_OWNER = "LukeSavefrogs"
REPO_NAME = "danea-easyfatt"

logger = logging.getLogger("danea-easyfatt.updater")
logger.addHandler(logging.NullHandler())


def get_latest_version():
	response = requests.get(f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest")
	json_response = json.loads(response.text)

	return { 
		"url": json_response["html_url"],
		"version": json_response["tag_name"],
		"date": json_response["published_at"]
	}


def get_current_version():
	toml_file = find_toml_file()

	if not toml_file.exists() or not toml_file.is_file():
		raise Exception(f"Update error: TOML file '{toml_file}' was not found.")

	poetry_config = toml.load(toml_file)

	return poetry_config["tool"]["poetry"]["version"]


def update_available():
	latest  = Version(get_latest_version()["version"])
	current = Version(get_current_version())
	
	logger.debug(f"Latest is {latest}")
	logger.debug(f"Current is {current}")

	return latest > current

def find_toml_file():
	"""Find the correct path to the `pyproject.toml` file.

	When bundled, the entry point is at top-level, so i need 
	to adjust the path accordingly.

	Returns:
		pathlib.Path: Absolute path to the `pyproject.toml` file.
	"""
	bundle_directory = Path(bundle.get_bundle_directory())

	if bundle.is_executable():
		return (bundle_directory / 'pyproject.toml').resolve()

	return (bundle_directory / '..' / 'pyproject.toml').resolve()



if __name__ == '__main__':
	toml_file = find_toml_file()
	logger.info(f"TOML File: '{toml_file}'")


	if not toml_file.exists() or not toml_file.is_file():
		logger.critical(f"File '{toml_file}' does not exist!")
		sys.exit(1)


	if update_available():
		logger.warning(f"An update is available (remote is '{Version(get_latest_version()['version'])}', while current is '{Version(get_current_version())}')")
	else:
		logger.info(f"You're already running the latest version.")