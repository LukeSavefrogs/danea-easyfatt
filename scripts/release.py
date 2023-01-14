# git add pyproject.toml
# git commit -m v$(poetry version -s) # prints out the project version
# git tag v$(poetry version -s)

# # Push the version information
# git push origin master # Or your current branch
# git push origin --tags # Push the tags

import subprocess
from rich.logging import RichHandler
import logging



logger = logging.getLogger(__name__)
logger.addHandler(RichHandler(
	rich_tracebacks=True,
	omit_repeated_times=False,
	log_time_format="[%d-%m-%Y %H:%M:%S]"
))
logger.setLevel(logging.DEBUG)


from pathlib import Path
import git

def main():
	current_repo_dir = Path(".").resolve()
	repo = git.Repo(current_repo_dir)

	poetry_version_data = subprocess.run(
		['poetry', 'version', '--short'], 
		stdout=subprocess.PIPE
	)

	file_version = (poetry_version_data.stdout).decode('UTF-8').strip()
	version = f"v{file_version}"

	tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
	latest_tag = tags[-1]

	changed_files = [ item.a_path for item in repo.index.diff(None) ]

	modifiche_non_committate = repo.index.diff('Head')
	if len(modifiche_non_committate) > 0:
		logger.critical(f"Ci sono {len(modifiche_non_committate)} modifiche non ancora committate.")
		return False

	logger.debug("File modificati: \n\t- " + '\n\t- '.join(changed_files))
	logger.debug("File non tracciati: \n\t- " + '\n\t- '.join(repo.untracked_files))

	if len(repo.untracked_files) > 0:
		logger.warning(f"Attenzione: Ci sono {len(repo.untracked_files)} file non tracciati.")

	if str(latest_tag) == str(version):
		logger.error(f"Tag '{version}' già esistente.")
		return False

	input(f"Premi [INVIO] per pubblicare la versione '{version}'...")

	logger.info(f"Creo release per la versione '{version}' (latest: '{latest_tag}')")

	try:
		tag = repo.create_tag(
			path=version,
			message=f"Aggiornamento alla versione {version}"
		)

		repo.remote('origin').push(tag.name)
		logger.info("Upload terminato con successo!")
	except git.exc.GitCommandError as e:
		logger.error(f"Creazione tag '{version}' fallita!")

if __name__ == '__main__':
	main()