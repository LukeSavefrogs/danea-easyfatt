import logging
import os
import re
import sys
import time
from functools import total_ordering

import requests
import json

import toml
from packaging.version import Version

import veryeasyfatt.bundle.path as bundle

logger = logging.getLogger("danea-easyfatt.updater")
logger.addHandler(logging.NullHandler())


@total_ordering
class GithubRelease(object):
    def __init__(self, url: str, version: str, date: str):
        self.url = url
        self.version = version
        self.date = date
        self._parsed_version = Version(version)

    def __str__(self):
        return f"{self.version} ({self.date})"

    def __repr__(self):
        return f"GithubRelease(version='{self.version}', date='{self.date}', url='{self.url}')"

    def _coerce_to_version(self, other):
        if isinstance(other, GithubRelease):
            return other._parsed_version
        if isinstance(other, Version):
            return other
        return NotImplemented

    def __eq__(self, other):
        other_version = self._coerce_to_version(other)
        if other_version is NotImplemented:
            return NotImplemented
        return self._parsed_version == other_version

    def __lt__(self, other):
        other_version = self._coerce_to_version(other)
        if other_version is NotImplemented:
            return NotImplemented
        return self._parsed_version < other_version


def get_github_token() -> str:
    """Returns the Github token to use for API requests.

    The token is read from the `GITHUB_TOKEN` environment variable.

    Raises:
        Exception: If the `GITHUB_TOKEN` environment variable is not set or is empty.

    Returns:
        token (str): The Github token
    """
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if token == "":
        raise Exception(
            "The 'GITHUB_TOKEN' environment variable is not set or is empty."
        )
    return token


def get_github_api_endpoint() -> str:
    """Returns the current project's Github API endpoint.

    Uses the `pyproject.toml` file in the root folder of the project to determine the repository URL.

    Raises:
        Exception: If the URL is not a valid Github repository URL

    Returns:
        api_url (str): The URL of the REST API endpoint
    """
    repository_url = (
        toml.load((bundle.get_root_directory() / "pyproject.toml").resolve())
        .get("tool", {})
        .get("poetry", {})
        .get("repository", "")
    )

    url = re.match(
        r"(?:(?:https?:)?//)?(github.com)/([-A-Za-z0-9_.]+)/([-A-Za-z0-9_.]+)",
        repository_url,
    )

    if url is None or len(url.groups()) != 3:
        raise Exception(
            f"The URL '{repository_url}' is not a valid Github repository URL."
        )

    (domain, author, repository) = url.groups()
    return f"https://api.{domain}/repos/{author}/{repository}"


def get_latest_release() -> GithubRelease:
    """Returns information about the latest release (/releases/latest).

    Returns:
        release (GithubRelease): The release information
    """
    api_url = get_github_api_endpoint()
    extra_headers = {}

    try:
        extra_headers["Authorization"] = f"Token {get_github_token()}"
    except Exception:
        logger.debug(f"Could not retrieve Github token")

    try:
        response = requests.get(
            f"{api_url}/releases/latest",
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                # Add a custom User-Agent to identify the application making the request, as recommended by GitHub's API guidelines
                # https://docs.github.com/en/rest/using-the-rest-api/getting-started-with-the-rest-api?apiVersion=2022-11-28#user-agent
                "User-Agent": f"{'/'.join(api_url.split('/')[-2:])} - VeryEasyfatt Updater",
                **extra_headers,
            },
        )
        response.raise_for_status()
    except requests.HTTPError as e:
        if response.status_code in [403, 429]:
            retry_after = int(response.headers.get("Retry-After", -1))
            x_rate_limit_remaining = int(
                response.headers.get("X-RateLimit-Remaining", -1)
            )

            # The `x-ratelimit-reset` header is in UTC epoch seconds.
            x_rate_limit_reset = int(response.headers.get("X-RateLimit-Reset", -1))
            logger.warning(
                f"Github API rate limit exceeded: retry after={retry_after}, remaining={x_rate_limit_remaining} (resets at {x_rate_limit_reset})."
            )

            if retry_after > 0:
                # Retry after waiting the specified time
                logger.info(f"Waiting for {retry_after} seconds before retrying...")
                time.sleep(retry_after)
                return get_latest_release()

            if x_rate_limit_remaining == 0 and x_rate_limit_reset > 0:
                # Calculate the time to wait until the rate limit resets
                current_time = int(time.time())
                wait_time = x_rate_limit_reset - current_time
                if wait_time > 0:
                    rate_limit_reset = time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.gmtime(x_rate_limit_reset)
                    )
                    logger.info(
                        f"Waiting for {wait_time} seconds until rate limit resets (at {rate_limit_reset} UTC)..."
                    )
                    time.sleep(wait_time)
                    return get_latest_release()

        logger.error(f"HTTP error occurred: {e}")
        raise

    json_response = json.loads(response.text)

    return GithubRelease(
        url=json_response["html_url"],
        version=json_response["tag_name"],
        date=json_response["published_at"],
    )


def get_latest_version() -> str:
    """Returns the latest version available from the releases.

    Returns:
        version (str): The remote version
    """
    return get_latest_release().version


def get_current_version() -> str:
    """Returns the current version as specified in the `pyproject.toml` under `tool.poetry.version`.

    Raises:
        Exception: If the `pyproject.toml` cannot be found

    Returns:
        version (str): The current version
    """
    toml_file = (bundle.get_root_directory() / "pyproject.toml").resolve()

    if not toml_file.exists() or not toml_file.is_file():
        raise Exception(f"Update error: TOML file '{toml_file}' was not found.")

    poetry_config = toml.load(toml_file)

    return poetry_config["tool"]["poetry"]["version"]


def update_available() -> bool:
    """Checks if a new version has been released.

    Returns:
        is_available (bool): Wether a new update is available among the releases.
    """
    latest = Version(get_latest_version())
    current = Version(get_current_version())

    logger.debug(f"Latest is {latest}")
    logger.debug(f"Current is {current}")

    return latest > current


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s] %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    toml_file = (bundle.get_root_directory() / "pyproject.toml").resolve()
    logger.info(f"TOML File: '{toml_file}'")

    if not toml_file.exists() or not toml_file.is_file():
        logger.critical(f"File '{toml_file}' does not exist!")
        sys.exit(1)

    if update_available():
        logger.warning(
            f"An update is available (remote is '{Version(get_latest_version())}', while current is '{Version(get_current_version())}')"
        )
    else:
        logger.info(f"You're already running the latest version.")
