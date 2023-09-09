from pathlib import Path as _Path

from dynaconf import Dynaconf as _Dynaconf

from veryeasyfatt.shared.merging import deepmerge as _deepmerge


class Dynaconf(_Dynaconf):
    def reload_settings(self, filename: str | _Path, validate=True) -> None:
        """Update the settings using the given file.

        Implements a custom merging strategy to merge the new
        settings with the old ones (see [#999](https://github.com/dynaconf/dynaconf/issues/999)).

        Args:
            filename (str|Path): The path of the file to load.
            validate (bool, optional): Whether to validate the settings after updating them. Defaults to True.
        """
        new_settings = Dynaconf(settings_files=[filename]).to_dict()
        old_settings = self.to_dict()

        new_settings_dict = _deepmerge(old_settings, new_settings)
        self.update(new_settings_dict, merge=False, validate=validate)
