import logging
import re
import sys

import requests
import json

import toml
from packaging.version import Version

import bundle.path as bundle

logger = logging.getLogger("danea-easyfatt.updater")
logger.addHandler(logging.NullHandler())


def get_github_api_endpoint() -> str:
	""" Returns the current project's Github API endpoint.

	Uses the `pyproject.toml` file in the root folder of the project to determine the repository URL.

	Raises:
		Exception: If the URL is not a valid Github repository URL

	Returns:
		api_url (str): The URL of the REST API endpoint
	"""
	repository_url = toml.load((bundle.get_root_directory() / 'pyproject.toml').resolve()) \
		.get("tool", {}) \
		.get("poetry", {}) \
		.get("repository", "")

	url = re.match(r"(?:(?:https?:)?//)?(github.com)/([-A-Za-z0-9_.]+)/([-A-Za-z0-9_.]+)", repository_url)

	if url is None or len(url.groups()) != 3:
		raise Exception(f"The URL '{repository_url}' is not a valid Github repository URL.")
	
	(domain, author, repository) = url.groups()
	return f"https://api.{domain}/repos/{author}/{repository}"


def get_latest_release():
	""" Returns information about the latest release (/releases/latest).

	Returns:
		release (dict): The release information
	"""
	api_url = get_github_api_endpoint()

	response = requests.get(f"{api_url}/releases/latest")
	json_response = json.loads(response.text)

	return { 
		"url": json_response["html_url"],
		"version": json_response["tag_name"],
		"date": json_response["published_at"]
	}

def get_latest_version() -> str:
	""" Returns the latest version available from the releases.

	Returns:
		version (str): The remote version
	"""
	return get_latest_release()["version"]


def get_current_version() -> str:
	""" Returns the current version as specified in the `pyproject.toml` under `tool.poetry.version`.

	Raises:
		Exception: If the `pyproject.toml` cannot be found

	Returns:
		version (str): The current version
	"""
	toml_file = (bundle.get_root_directory() / 'pyproject.toml').resolve()

	if not toml_file.exists() or not toml_file.is_file():
		raise Exception(f"Update error: TOML file '{toml_file}' was not found.")

	poetry_config = toml.load(toml_file)

	return poetry_config["tool"]["poetry"]["version"]


def update_available() -> bool:
	""" Checks if a new version has been released.

	Returns:
		is_available (bool): Wether a new update is available among the releases.
	"""
	latest  = Version(get_latest_version())
	current = Version(get_current_version())
	
	logger.debug(f"Latest is {latest}")
	logger.debug(f"Current is {current}")

	return latest > current


if __name__ == '__main__':
	toml_file = (bundle.get_root_directory() / 'pyproject.toml').resolve()
	logger.info(f"TOML File: '{toml_file}'")


	if not toml_file.exists() or not toml_file.is_file():
		logger.critical(f"File '{toml_file}' does not exist!")
		sys.exit(1)


	if update_available():
		logger.warning(f"An update is available (remote is '{Version(get_latest_version())}', while current is '{Version(get_current_version())}')")
	else:
		logger.info(f"You're already running the latest version.")