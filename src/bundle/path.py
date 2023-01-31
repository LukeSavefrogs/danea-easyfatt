import sys
from pathlib import Path
import inspect

def get_bundle_directory() -> str:
	"""Returns the directory where the script is located (or bundled).
	
	Works either with a `pyinstaller` bundled app or a normal Python script.

	Returns:
		bool: The directory as a string.
	"""
	if is_executable():
		# we are running in a bundle
		return Path(sys._MEIPASS).resolve().absolute()
	else:
		# we are running in a normal Python environment
		caller_file = inspect.stack()[1].filename
		return Path(caller_file).resolve().absolute().parent


def is_executable() -> bool:
	"""Checks wether the app has been bundled using `pyinstaller` or not (normal Python environment).
	
	Source:
		https://pyinstaller.org/en/stable/runtime-information.html#run-time-information
	
	Returns:
		bool: `True` if the script is bundled in an executable.
	"""
	return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def get_root_directory(ref_filename: str = "pyproject.toml"):
	"""Find the correct path to the root of the bundle.

	When bundled, the entry point is at top-level, so i need 
	to adjust the path accordingly.

	Arguments:
		ref_filename(str): File name used placed in the root directory to use as a reference.

	Returns:
		pathlib.Path | None: Absolute path to the `pyproject.toml` file.
	"""
	bundle_directory = Path(get_bundle_directory())

	return find_upwards(bundle_directory, ref_filename).parent


def find_upwards(cwd: Path, filename: str):
	"""Recursively searches for `filename` into `cwd` and all directories above it.
	
	The search goes on until it finds the first occurrence.

	Args:
		cwd (Path): _description_
		filename (str): _description_

	Returns:
		_type_: _description_
	"""
	if cwd == Path(cwd.root) or cwd == cwd.parent:
		return None
	
	fullpath = cwd / filename
	
	return fullpath if fullpath.exists() else find_upwards(cwd.parent, filename)