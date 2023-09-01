""" This module contains functions used to abstract away the differences when
bundled with Pyinstaller or executed directly with Python.
"""
from .path import *

__ALL__ = ["get_bundle_directory", "is_executable"]
