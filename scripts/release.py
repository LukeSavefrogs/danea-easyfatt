import logging
from rich.logging import RichHandler

from pathlib import Path
import git

import toml
import requests

from random import randint

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

	current_branch = repo.active_branch.name

	local_toml_file  = (Path(".") / 'pyproject.toml').resolve()
	remote_toml_file = f"https://raw.githubusercontent.com/LukeSavefrogs/danea-easyfatt/{current_branch}/pyproject.toml?nocache={randint(0, 123456)}"
	
	logger.debug(f"Requesting '{remote_toml_file}'")
	try:
		remote_toml_file_content = requests.get(remote_toml_file, headers={
			"Cache-Control": "no-cache",
			"Pragma": "no-cache"
		}).text
	except Exception as e:
		logger.critical(f"Errore in fase di recupero versione remota: {repr(e)}")
		return False

	if not local_toml_file.exists() or not local_toml_file.is_file():
		logger.fatal(f"File TOML '{local_toml_file}' non trovato.")
		return False

	local_poetry_config  = toml.load(local_toml_file)
	remote_poetry_config = toml.loads(remote_toml_file_content)

	local_version  = "v" + local_poetry_config["tool"]["poetry"]["version"]
	remote_version = "v" + remote_poetry_config["tool"]["poetry"]["version"]

	logger.info(f"Versione `pyproject.toml` locale: '{local_version}'")
	logger.info(f"Versione `pyproject.toml` remoto: '{remote_version}'")

	
	if local_version != remote_version:
		logger.critical("Prima di eseguire la release il file `pyproject.toml` deve essere SEMPRE aggiornato.")
		logger.warning("Assicurarsi di pushare la nuova versione.")
		return False


	local_tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
	latest_tag = local_tags[-1]

	logger.info(f"Ultima versione rilasciata: '{latest_tag}'")

	changed_files = [ item.a_path for item in repo.index.diff(None) ]

	uncommitted_changes = repo.index.diff('Head')
	if len(uncommitted_changes) > 0:
		logger.critical(f"Ci sono {len(uncommitted_changes)} modifiche non ancora committate.")
		return False

	unpushed_commits = list(repo.iter_commits(current_branch + '@{u}..' + current_branch))
	if unpushed_commits:
		logger.critical(f"Ci sono {len(unpushed_commits)} commit da pushare.")
		for commit in unpushed_commits:
			commit_time    = commit.committed_datetime.strftime('%d-%m-%Y %H:%M:%S')
			commit_hash    = commit.hexsha[-6:]
			commit_message = commit.message.strip().splitlines()[0]
			print(f"- [{commit_time}] {commit_hash} ➜ {commit_message}")
		
		print("")
		logger.warning(f"Esegui il comando 'git push' e ritenta.")

		return False

	logger.debug("File modificati: \n\t- " + '\n\t- '.join(changed_files))
	logger.debug("File non tracciati: \n\t- " + '\n\t- '.join(repo.untracked_files))

	if len(repo.untracked_files) > 0:
		logger.warning(f"Attenzione: Ci sono {len(repo.untracked_files)} file non tracciati.")

	if str(latest_tag) == str(local_version):
		logger.error(f"Tag '{local_version}' già esistente.\nAumenta il numero di versione con 'poetry version [patch/minor/major/prepatch/preminor/premajor/prerelease]'")
		return False

	input(f"Premi [INVIO] per pubblicare la versione '{local_version}'...")

	logger.info(f"Creo release per la versione '{local_version}' (latest: '{latest_tag}')")
	# logger.info(f"Creo release per la commit '{repo.head.commit}'")

	try:
		tag = repo.create_tag(
			# ref=repo.head.commit,
			# force=True,
			path=local_version,
			message=f"Aggiornamento alla versione {local_version}"
		)

		logger.debug(f"Lancio comando push per tag '{tag.name}'")
		repo.remote('origin').push(tag.name)
		logger.info("Upload terminato con successo!")
	except git.exc.GitCommandError as e:
		logger.error(f"Creazione tag '{local_version}' fallita!")

if __name__ == '__main__':
	main()