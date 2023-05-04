import unittest

import updater
from packaging.version import Version

class OperationsTestCase(unittest.TestCase):
	def test_current_version (self):
		self.assertRegex(
			updater.get_current_version(),
			r"[0-9]+\.[0-9]+\.[0-9]+.*"
		)

	def test_remote_release (self):
		version_info = updater.get_latest_release()

		self.assertEqual(len(version_info.keys()), 3)
		
		self.assertRegex(
			version_info["version"],
			r"[0-9]+\.[0-9]+\.[0-9]+.*"
		)
	
	def test_remote_version (self):
		version_info = updater.get_latest_version()

		self.assertRegex(
			version_info,
			r"[0-9]+\.[0-9]+\.[0-9]+.*"
		)
	
	def test_version_syntax (self):
		latest  = Version(updater.get_latest_version())
		current = Version(updater.get_current_version())

		self.assertIsInstance(latest, Version)
		self.assertIsInstance(current, Version)