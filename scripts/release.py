import random
import requests
from pathlib import Path

import logging
from rich.logging import RichHandler
import rich

from git.exc import GitCommandError
from git.repo import Repo

import toml
from urllib.parse import urlparse
from packaging.version import Version

logger = logging.getLogger(__name__)
logger.addHandler(
    RichHandler(
        rich_tracebacks=True,
        omit_repeated_times=False,
        log_time_format="[%d-%m-%Y %H:%M:%S]",
    )
)
logger.setLevel(logging.DEBUG)


def release(
    owner: str | None = None,
    repo: str | None = None,
    branch: str | None = None,
    check_changelog: bool = True,
):
    """Release a new version of the project.

    This function will check if the local repository is aligned with the remote one.
    If the local repository is aligned, it will create a new tag and push it to the remote.

    If properly configured, it will also check if the `CHANGELOG.md` file has been updated.

    Args:
        owner (str, optional): The owner of the repository. Defaults to None.
        repo (str, optional): The name of the repository. Defaults to None.
        branch (str, optional): The name of the branch. Defaults to None.
        check_changelog (bool, optional): Check if the `CHANGELOG.md` file has been updated. Defaults to True.
    """
    console = rich.console.Console()

    current_repo_dir = Path(".").resolve()
    repository = Repo(current_repo_dir)

    if branch is None:
        branch = repository.active_branch.name

    # 1. Read local "pyproject.toml" file
    local_toml_file = (Path(".") / "pyproject.toml").resolve()
    if not local_toml_file.exists() or not local_toml_file.is_file():
        logger.fatal(f"File TOML '{local_toml_file}' couldn't be found.")
        return False

    local_poetry_config = toml.load(local_toml_file)

    repository_url = urlparse(local_poetry_config["tool"]["poetry"]["repository"])
    if repository_url.netloc != "github.com":
        logger.fatal(f"Website '{repository_url}' is currently not supported.")
        return False

    repository_info = repository_url.path.strip("/").split("/")[:2]
    if owner is None:
        owner = repository_info[0]
    if repo is None:
        repo = repository_info[1]

    remote_toml_file = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/pyproject.toml?nocache={random.randint(0, 123456)}"

    # 2. Read remote "pyproject.toml" file
    try:
        remote_toml_file_content = requests.get(
            remote_toml_file,
            headers={"Cache-Control": "no-cache", "Pragma": "no-cache", "Expires": "0"},
        ).text
    except Exception as e:
        logger.critical(f"Error while fetching the remote TOML file: {repr(e)}")
        return False

    remote_poetry_config = toml.loads(remote_toml_file_content)

    # 3. Compare TOML files versions (must be both equal)
    version_local = "v" + local_poetry_config["tool"]["poetry"]["version"]
    version_remote = "v" + remote_poetry_config["tool"]["poetry"]["version"]

    logger.debug(f"Local  → `pyproject.toml` version : '{version_local}'")
    logger.debug(f"Remote → `pyproject.toml` version: '{version_remote}'")

    if version_local != version_remote:
        logger.critical(
            "Before releasing the file `pyproject.toml` MUST ALWAYS BE UPDATED."
        )
        logger.warning("Please push the new version and retry.")
        return False

    logger.info(f"TOML files are aligned with version '{version_local}'")

    # EXTRA: Check if `CHANGELOG.md` has been updated
    if check_changelog:
        changelog_file = (Path(".") / "CHANGELOG.md").resolve()
        if not changelog_file.exists() or not changelog_file.is_file():
            logger.fatal(f"File 'CHANGELOG.md' couldn't be found.")
            return False

        changed_content = changelog_file.read_text()
        if "## [Unreleased]" in changed_content:
            logger.critical(
                f"File 'CHANGELOG.md' still has an '## [Unreleased]' section."
            )
            return False

        if f"## [{version_local}]" not in changed_content:
            logger.critical(
                f"File 'CHANGELOG.md' does NOT have the '## [{version_local}]' section."
            )
            return False

    # 4. Check if the tags are aligned
    latest_tag_local = sorted(
        repository.tags, key=lambda t: t.commit.committed_datetime
    )[-1]
    try:
        latest_tag_remote = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/tags?nocache={random.randint(0, 123456)}",
            headers={"Cache-Control": "no-cache", "Pragma": "no-cache", "Expires": "0"},
        ).json()[0]["name"]
    except Exception as e:
        logger.critical(f"Error while fetching the remote tags: {repr(e)}")
        return False

    logger.info(f"Local  → Latest tag: '{latest_tag_local}'")
    logger.info(f"Remote → Latest tag: '{latest_tag_remote}'")

    if Version(str(latest_tag_local)) < Version(latest_tag_remote):
        logger.error(
            f"Remote repository has newer tag: '{latest_tag_remote}' (local is '{latest_tag_local}')."
        )
        return False

    # 5. Check if there are uncommitted changes
    changed_files = [item.a_path for item in repository.index.diff(None)]

    uncommitted_changes = repository.index.diff("Head")
    if len(uncommitted_changes) > 0:
        logger.critical(
            f"There are {len(uncommitted_changes)} uncommitted changes! Please commit them before releasing."
        )
        return False

    # 6. Check if there are unpushed commits (both modified and untracked files)
    unpushed_commits = list(repository.iter_commits(branch + "@{u}.." + branch))
    if unpushed_commits:
        logger.critical(
            f"There are {len(unpushed_commits)} commits that need to be pushed to the remote."
        )
        for commit in unpushed_commits:
            commit_time = commit.committed_datetime.strftime("%d-%m-%Y %H:%M:%S")
            commit_hash = commit.hexsha[-6:]
            commit_message = str(commit.message).strip().splitlines()[0]
            print(f"- [{commit_time}] {commit_hash} → {commit_message}")

        print("")
        logger.warning(f"Please run 'git push' and retry...")
        return False

    print("")
    if changed_files:
        console.print(
            f"⚠️  You have uncommitted changes on {len(changed_files)} files:"
        )
        for file in changed_files:
            console.print(f"\t- {Path(file)}")
    else:
        print("✔️  No uncommitted changes found.")

    print("")

    if repository.untracked_files:
        console.print(f"📄 There are {len(repository.untracked_files)} untracked files:")
        for file in repository.untracked_files:
            console.print(f"\t- {Path(file)}")
        print("")
        logger.warning(f"There are {len(repository.untracked_files)} untracked files.")
    else:
        print("✔️  No untracked files found.")
        print("")

    # 7. Check if a tag with the current version already exists
    if str(latest_tag_local) == str(version_local):
        logger.critical(f"Tag '{version_local}' already exists.")
        print("")
        console.print(
            "HINT - You can increment the version number using one of the following:"
        )
        for release_type in [
            "major",
            "minor",
            "patch",
            "premajor",
            "preminor",
            "prepatch",
            "prerelease",
        ]:
            console.print(f"\t▶ poetry version {release_type}")
        return False

    input(f"Press [ENTER] to release version '{version_local}'...")

    # 9. Create a new tag and push it to the remote
    logger.info(
        f"Creating release for version '{version_local}' (latest: '{latest_tag_local}')"
    )
    try:
        tag = repository.create_tag(
            path=version_local,
            message=f"Aggiornamento alla versione {version_local}",
        )

        logger.debug(f"Pushing tag '{tag.name}' to remote")
        repository.remote("origin").push(tag.name)
        logger.info("Upload ended successfully!")
    except GitCommandError as e:
        logger.error(f"Error while trying to create tag '{version_local}': {repr(e)}")


if __name__ == "__main__":
    release()
