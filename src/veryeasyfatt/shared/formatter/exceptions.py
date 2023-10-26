class SimpleFormatterError(Exception):
    """Base exception for the `SimpleFormatter` package."""


class UnknownCommandError(SimpleFormatterError):
    """Exception raised when the command is not recognized."""


class InvalidFormatError(SimpleFormatterError):
    """Exception raised when the format string is invalid."""
