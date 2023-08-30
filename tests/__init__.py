import unittest

# Hides Docstring from Verbosis mode (see https://stackoverflow.com/a/69395163/8965861)
unittest.TestCase.shortDescription = lambda self: None # type: ignore