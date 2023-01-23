import os, sys
import inspect

def get_bundle_directory() -> str:
	"""Returns the directory where the script is located (or bundled).
	
	Works either with a `pyinstaller` bundled app or a normal Python script.

	Returns:
		bool: The directory as a string.
	"""
	if is_executable():
		# we are running in a bundle
		return os.path.abspath(sys._MEIPASS)
	else:
		# we are running in a normal Python environment
		caller_file = inspect.stack()[1].filename
		return os.path.dirname(os.path.abspath(caller_file))


def is_executable() -> bool:
	"""Checks wether the app has been bundled using `pyinstaller` or not (normal Python environment).
	
	Source:
		https://pyinstaller.org/en/stable/runtime-information.html#run-time-information
	
	Returns:
		bool: `True` if the script is bundled in an executable.
	"""
	return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')