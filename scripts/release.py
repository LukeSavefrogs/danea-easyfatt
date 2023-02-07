# git add pyproject.toml
# git commit -m v$(poetry version -s) # prints out the project version
# git tag v$(poetry version -s)

# # Push the version information
# git push origin master # Or your current branch
# git push origin --tags # Push the tags

import logging
from rich.logging import RichHandler

from pathlib import Path
import git

import toml

logger = logging.getLogger(__name__)
logger.addHandler(RichHandler(
	rich_tracebacks=True,
	omit_repeated_times=False,
	log_time_format="[%d-%m-%Y %H:%M:%S]"
))
logger.setLevel(logging.DEBUG)


def main():
	current_repo_dir = Path(".").resolve()
	repo = git.Repo(current_repo_dir)

	toml_file = (Path(".") / 'pyproject.toml').resolve()

	if not toml_file.exists() or not toml_file.is_file():
		logger.fatal(f"File TOML '{toml_file}' non trovato.")
		return False

	poetry_config = toml.load(toml_file)

	version = "v" + poetry_config["tool"]["poetry"]["version"]
	logger.info(f"Versione da rilasciare: '{version}'")

	local_tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
	latest_tag = local_tags[-1]

	logger.info(f"Ultima versione rilasciata: '{latest_tag}'")

	changed_files = [ item.a_path for item in repo.index.diff(None) ]

	uncommitted_changes = repo.index.diff('Head')
	if len(uncommitted_changes) > 0:
		logger.critical(f"Ci sono {len(uncommitted_changes)} modifiche non ancora committate.")
		return False

	unpushed_commits = list(repo.iter_commits('main@{u}..main'))
	if unpushed_commits:
		logger.critical(f"Ci sono {len(unpushed_commits)} commit da pushare.")
		for commit in unpushed_commits:
			commit_time = commit.committed_datetime.strftime('%d-%m-%Y %H:%M:%S')
			short_sha = commit.hexsha[-6:]
			print(f"- [{commit_time}] {short_sha} ➜ {commit.message.strip()}")
		
		print("")

		logger.info(f"Esegui il comando 'git push' e ritenta.")

		return False

	logger.debug("File modificati: \n\t- " + '\n\t- '.join(changed_files))
	logger.debug("File non tracciati: \n\t- " + '\n\t- '.join(repo.untracked_files))

	if len(repo.untracked_files) > 0:
		logger.warning(f"Attenzione: Ci sono {len(repo.untracked_files)} file non tracciati.")

	if str(latest_tag) == str(version):
		logger.error(f"Tag '{version}' già esistente.\nAumenta il numero di versione con 'poetry version [patch/minor/major/prepatch/preminor/premajor/prerelease]'")
		return False

	input(f"Premi [INVIO] per pubblicare la versione '{version}'...")

	logger.info(f"Creo release per la versione '{version}' (latest: '{latest_tag}')")
	# logger.info(f"Creo release per la commit '{repo.head.commit}'")

	try:
		tag = repo.create_tag(
			# ref=repo.head.commit,
			# force=True,
			path=version,
			message=f"Aggiornamento alla versione {version}"
		)

		logger.debug(f"Lancio comando push per tag '{tag.name}'")
		repo.remote('origin').push(tag.name)
		logger.info("Upload terminato con successo!")
	except git.exc.GitCommandError as e:
		logger.error(f"Creazione tag '{version}' fallita!")

if __name__ == '__main__':
	main()