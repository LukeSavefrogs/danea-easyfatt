import unittest
from veryeasyfatt.shared.merging import deepmerge


class MergerTestCase(unittest.TestCase):
    # Do not use the docstring as the test name.
    shortDescription = lambda self: None

    def test_nochanges(self):
        """Test that the merger does not change the input in case the two dictionaries are equal."""
        self.assertEqual(
            deepmerge(
                {
                    "a": 1,
                    "b": 2,
                    "c": {
                        "d": 3,
                        "e": 4,
                        "f": {
                            "g": 5,
                            "h": 6,
                        },
                    },
                },
                {
                    "a": 1,
                    "b": 2,
                    "c": {
                        "d": 3,
                        "e": 4,
                        "f": {
                            "g": 5,
                            "h": 6,
                        },
                    },
                },
            ),
            {
                "a": 1,
                "b": 2,
                "c": {
                    "d": 3,
                    "e": 4,
                    "f": {
                        "g": 5,
                        "h": 6,
                    },
                },
            },
        )

    def test_replace(self):
        """The merger should replace the values in the first dictionary with the ones in the second."""
        self.assertEqual(
            deepmerge(
                {
                    "a": 1,
                    "b": True,
                },
                {
                    "a": 2,
                    "b": False,
                },
            ),
            {
                "a": 2,
                "b": False,
            },
        )

    def test_add(self):
        """The merger should add the values in the second dictionary to the first if they do not exist."""
        self.assertEqual(
            deepmerge(
                {
                    "a": 1,
                    "b": 2,
                },
                {
                    "b": 2,
                    "c": 3,
                    "d": 4,
                },
            ),
            {
                "a": 1,
                "b": 2,
                "c": 3,
                "d": 4,
            },
        )
        self.assertEqual(
            deepmerge(
                {
                    "a": 1,
                    "b": 2,
                },
                {
                    "c": 3,
                    "d": 4,
                },
            ),
            {
                "a": 1,
                "b": 2,
                "c": 3,
                "d": 4,
            },
        )

    def test_lists(self):
        """The merger should merge lists correctly."""
        self.assertEqual(
            deepmerge(
                {
                    "a": [1, 2, 3],
                    "b": 2,
                },
                {
                    "a": [1, 2, 3],
                    "b": 2,
                },
            ),
            {
                "a": [1, 2, 3],
                "b": 2,
            },
        )
        self.assertEqual(
            deepmerge(
                {
                    "a": [1, 2, 3],
                    "b": 2,
                },
                {
                    "a": [1, 10, 3],
                    "b": 9,
                },
            ),
            {
                "a": [1, 10, 3],
                "b": 9,
            },
        )

    def test_different_types(self):
        """The merger should merge different types without issues."""
        self.assertEqual(
            deepmerge(
                {
                    "a": 1,
                    "b": 2,
                },
                {
                    "a": [1, 2, 3],
                    "b": True,
                },
            ),
            {
                "a": [1, 2, 3],
                "b": True,
            },
        )
        self.assertEqual(
            deepmerge(
                {
                    "a": 1,
                    "b": {"c": 2},
                },
                {
                    "a": "1",
                    "b": True,
                },
            ),
            {
                "a": "1",
                "b": True,
            },
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
