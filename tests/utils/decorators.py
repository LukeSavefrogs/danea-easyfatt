import functools
import os
from pathlib import Path
import tempfile


def with_temporary_file(file_prefix="veryeasyfatt-", file_suffix=".config.toml", *args, **kwargs):
    """ Create a temporary file before the test starts and passes the file path as the first parameter.
        At the end it deletes the temporary file 
    """
    def decorator(decorated_function):
        @functools.wraps(decorated_function)
        def wrapper(self):
            """ Wrapper around the test method. """
            # Create temporary file
            (fd, temp_file) = tempfile.mkstemp(prefix=file_prefix, suffix=file_suffix, text=True)
            os.close(fd)   # The file handler is kept open by mkstemp, so close it.

            temp_config_file = Path(temp_file).resolve()    # Convert it to `pathlib.Path`

            try:
                # Execute the test by passing the configuration file path as the first parameter
                decorated_function(self, temp_config_file, *args, **kwargs)
            except Exception:
                raise
            finally:
                temp_config_file.unlink()
        return wrapper

    return decorator