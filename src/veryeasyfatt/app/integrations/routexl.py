import re

REGEX_TIME_BOUNDARY_INTERVAL = (
    r"(?P<start>[0-9:]+)"
    r"\s*(?P<separator>>+|-+|\s+(?:a|to)\s+)\s*"
    r"(?P<end>[0-9:]+)"
)


class RouteXLTimeBoundary:
    def __init__(self, ready_time: str, due_time: str):
        self.ready_time = ready_time
        self.due_time = due_time

    def __str__(self):
        return f"{self.ready_time}>>{self.due_time}"

    @classmethod
    def from_string(cls, string: str):
        """Parse a time range string and create a RouteXLTimeBoundary instance.

        Supported formats:
            - `08 > 16` or `8 >> 16` (with or without spaces)
            - `08 - 16` or `8 -- 16` (with or without spaces)
            - `08 a 16` or `8 to 16` (spaces are mandatory)

        Args:
            string (str): A time range string, e.g., "08:00 > 16:00" or "8 >> 16".

        Returns:
            RouteXLTimeBoundary: A new instance with parsed ready_time and due_time.

        Raises:
            ValueError: If the input is not a string or doesn't match the expected format.
        """
        if not isinstance(string, str):
            raise ValueError(
                f"Input string must be of type 'str', not '{type(string).__name__}'"
            )

        intervallo_match = re.match(REGEX_TIME_BOUNDARY_INTERVAL, string)
        if intervallo_match is None:
            raise ValueError(
                f"String '{string}' does not match expected format for time boundaries."
            )

        ready_time, due_time = map(format_time, intervallo_match.group("start", "end"))
        return cls(ready_time=ready_time, due_time=due_time)


def format_time(value):
    """Format time string to ensure it has a leading zero and is in the format HH:MM.

    Args:
        value (str): The time string to format, e.g., "8:30" or "8".

    Returns:
        str: The formatted time string, e.g., "08:30" or "08:00".
    """
    orario = value.split(":")

    if len(orario) < 2:
        orario.append("0")

    return ":".join(map(lambda s: s.strip().zfill(2), orario))
