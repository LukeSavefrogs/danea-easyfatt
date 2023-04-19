""" Functions used to find files/directories in the context of applications
bundled with Pyinstaller. """

import sys
import inspect

from pathlib import Path


def is_executable() -> bool:
	"""Checks wether the app has been bundled using `pyinstaller` or not (normal Python environment).
	
	Source:
		https://pyinstaller.org/en/stable/runtime-information.html#run-time-information
	
	Returns:
		is_bundled (bool): `True` if the script is bundled in an executable.
	"""
	return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def get_bundle_directory() -> Path:
	"""Returns the directory where the script is located (or bundled).
	
	Works either with a `pyinstaller` bundled app or a normal Python script.

	Returns:
		bundle_directory (Path): The directory as a string.
	"""
	if is_executable():
		# we are running in a bundle
		return Path(getattr(sys, '_MEIPASS')).resolve().absolute()
	else:
		# we are running in a normal Python environment
		caller_file = inspect.stack()[1].filename
		return Path(caller_file).resolve().absolute().parent


def find_upwards(cwd: Path, filename: str) -> Path:
	"""Recursively searches for `filename` into `cwd` and all directories above it.
	
	The search goes on until it finds the first occurrence.

	Args:
		cwd (Path): The path where to start the search operation
		filename (str): The file name that has to be found

	Returns:
		path (Path): The desired path
	"""
	if cwd == Path(cwd.root) or cwd == cwd.parent:
		raise Exception("Reached root directory without finding the requested filename!")
	
	fullpath = cwd / filename
	
	return fullpath if fullpath.exists() else find_upwards(cwd.parent, filename)


def get_root_directory(ref_filename: str = "pyproject.toml") -> Path:
	"""Find the correct path to the root of the bundle.

	When bundled, the entry point is at top-level, so i need 
	to adjust the path accordingly.

	Arguments:
		ref_filename(str): File name used placed in the root directory to use as a reference.

	Returns:
		root_dir (pathlib.Path | None): Absolute path to the `pyproject.toml` file.
	"""
	bundle_directory = Path(get_bundle_directory())

	return find_upwards(bundle_directory, ref_filename).parent


def get_execution_directory() -> Path:
	"""Returns the directory where the actual script/executable is located.

	Source:
		https://stackoverflow.com/a/35514032/8965861

	Returns:
		execution_directory (Path): The path where the program is saved.
	"""
	return get_executed_file().parent


def get_executed_file() -> Path:
	"""Returns the absolute path to the script/executable being run.

	Returns:
		executed_file (Path): The path to the file being executed.
	"""
	return Path(sys.executable if is_executable() else sys.argv[0]).resolve().absolute()
