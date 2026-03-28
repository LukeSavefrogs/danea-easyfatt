import unittest

from veryeasyfatt.app.integrations.routexl import RouteXLTimeBoundary, format_time


class TestFormatTime(unittest.TestCase):
    """Tests for the format_time function."""

    def test_hour_only_single_digit(self):
        """Single digit hour should be zero-padded with :00 minutes."""
        self.assertEqual(format_time("8"), "08:00")

    def test_hour_only_double_digit(self):
        """Double digit hour should keep format with :00 minutes."""
        self.assertEqual(format_time("12"), "12:00")

    def test_hour_and_minutes_single_digit_hour(self):
        """Single digit hour with minutes should be zero-padded."""
        self.assertEqual(format_time("8:30"), "08:30")

    def test_hour_and_minutes_single_digit_minutes(self):
        """Single digit minutes should be zero-padded."""
        self.assertEqual(format_time("08:5"), "08:05")

    def test_hour_and_minutes_both_single_digit(self):
        """Both single digit hour and minutes should be zero-padded."""
        self.assertEqual(format_time("8:5"), "08:05")

    def test_already_formatted(self):
        """Already properly formatted time should remain unchanged."""
        self.assertEqual(format_time("08:30"), "08:30")

    def test_midnight(self):
        """Midnight should be formatted correctly."""
        self.assertEqual(format_time("0"), "00:00")

    def test_with_whitespace(self):
        """Whitespace around values should be stripped."""
        self.assertEqual(format_time(" 8 : 30 "), "08:30")


class TestRouteXLTimeBoundaryFromString(unittest.TestCase):
    """Tests for RouteXLTimeBoundary.from_string class method."""

    def test_single_arrow(self):
        """Parse time range with single arrow separator."""
        result = RouteXLTimeBoundary.from_string("08 > 16")
        self.assertEqual(result.ready_time, "08:00")
        self.assertEqual(result.due_time, "16:00")

    def test_double_arrow(self):
        """Parse time range with double arrow separator."""
        result = RouteXLTimeBoundary.from_string("8 >> 16")
        self.assertEqual(result.ready_time, "08:00")
        self.assertEqual(result.due_time, "16:00")

    def test_single_dash(self):
        """Parse time range with single dash separator."""
        result = RouteXLTimeBoundary.from_string("08 - 16")
        self.assertEqual(result.ready_time, "08:00")
        self.assertEqual(result.due_time, "16:00")

    def test_double_dash(self):
        """Parse time range with double dash separator."""
        result = RouteXLTimeBoundary.from_string("8 -- 16")
        self.assertEqual(result.ready_time, "08:00")
        self.assertEqual(result.due_time, "16:00")

    def test_italian_separator(self):
        """Parse time range with Italian 'a' separator."""
        result = RouteXLTimeBoundary.from_string("08 a 16")
        self.assertEqual(result.ready_time, "08:00")
        self.assertEqual(result.due_time, "16:00")

    def test_english_separator(self):
        """Parse time range with English 'to' separator."""
        result = RouteXLTimeBoundary.from_string("08 to 16")
        self.assertEqual(result.ready_time, "08:00")
        self.assertEqual(result.due_time, "16:00")

    def test_with_minutes(self):
        """Parse time range with minutes specified."""
        result = RouteXLTimeBoundary.from_string("08:30 > 16:45")
        self.assertEqual(result.ready_time, "08:30")
        self.assertEqual(result.due_time, "16:45")

    def test_no_spaces(self):
        """Parse time range without spaces around separator."""
        result = RouteXLTimeBoundary.from_string("08>16")
        self.assertEqual(result.ready_time, "08:00")
        self.assertEqual(result.due_time, "16:00")

    def test_str_representation(self):
        """String representation should use double arrow format."""
        result = RouteXLTimeBoundary.from_string("8 > 16")
        self.assertEqual(str(result), "08:00>>16:00")

    def test_invalid_type_raises_valueerror(self):
        """Non-string input should raise ValueError."""
        with self.assertRaises(ValueError) as context:
            RouteXLTimeBoundary.from_string(123)
        self.assertIn("must be of type 'str'", str(context.exception))

    def test_invalid_format_raises_valueerror(self):
        """Invalid format string should raise ValueError."""
        with self.assertRaises(ValueError) as context:
            RouteXLTimeBoundary.from_string("invalid")
        self.assertIn("does not match expected format", str(context.exception))

    def test_empty_string_raises_valueerror(self):
        """Empty string should raise ValueError."""
        with self.assertRaises(ValueError) as context:
            RouteXLTimeBoundary.from_string("")
        self.assertIn("does not match expected format", str(context.exception))


if __name__ == "__main__":
    unittest.main()
