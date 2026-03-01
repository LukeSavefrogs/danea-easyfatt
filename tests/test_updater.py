import unittest

import veryeasyfatt.updater as updater
from packaging.version import Version

class OperationsTestCase(unittest.TestCase):
	def test_current_version (self):
		self.assertRegex(
			updater.get_current_version(),
			r"[0-9]+\.[0-9]+\.[0-9]+.*"
		)

	def test_remote_release (self):
		version_info = updater.get_latest_release()

		self.assertIsInstance(version_info, updater.GithubRelease)
		
		self.assertRegex(
			version_info.version,
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


class GithubReleaseComparisonTestCase(unittest.TestCase):
	def _make_release(self, version: str) -> updater.GithubRelease:
		return updater.GithubRelease(url="https://example.com", version=version, date="2024-01-01")

	def test_compare_release_with_version_equal(self):
		release = self._make_release("1.2.3")
		self.assertEqual(release, Version("1.2.3"))

	def test_compare_release_with_version_less_than(self):
		release = self._make_release("1.2.3")
		self.assertLess(release, Version("1.2.4"))

	def test_compare_release_with_version_greater_than(self):
		release = self._make_release("1.2.4")
		self.assertGreater(release, Version("1.2.3"))

	def test_compare_version_with_release_equal(self):
		release = self._make_release("1.2.3")
		self.assertEqual(Version("1.2.3"), release)

	def test_compare_version_with_release_less_than(self):
		release = self._make_release("1.2.4")
		self.assertLess(Version("1.2.3"), release)

	def test_compare_version_with_release_greater_than(self):
		release = self._make_release("1.2.3")
		self.assertGreater(Version("1.2.4"), release)

	def test_compare_release_with_release_equal(self):
		release_a = self._make_release("1.2.3")
		release_b = self._make_release("1.2.3")
		self.assertEqual(release_a, release_b)

	def test_compare_release_with_release_less_than(self):
		release_a = self._make_release("1.2.3")
		release_b = self._make_release("1.2.4")
		self.assertLess(release_a, release_b)