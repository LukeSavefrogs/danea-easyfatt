from pathlib import Path
from dynaconf import Dynaconf, Validator

from veryeasyfatt import bundle
from veryeasyfatt.configuration.schemas import SettingsSchema


def _get_settings() -> Dynaconf:
    """FOR INTERNAL USE ONLY!

    Returns a `Dynaconf` object representing the application settings.
    This function can be used to test the configuration.

    Returns:
        Dynaconf: The application settings.

    Example:
        ```python
        from veryeasyfatt.configuration import _get_settings

        print(_get_settings() == _get_settings()) # False
    """
    return Dynaconf(
        settings_files=["veryeasyfatt.config.toml", ".secrets.toml"],
        merge_enabled=True,  # Merge all found files into one configuration.
        validate_on_update=False,  # Validate the configuration when it is updated.
        validators=[  # Custom validators.
            Validator(
                "easyfatt.database.filename",
                default=None,
                when=Validator("easyfatt.database.filename", eq=""),
                cast=lambda value: None
                if str(value).strip() == ""
                else Path(value).expanduser().resolve(),
            ),
            Validator(
                "files.input.easyfatt",
                default=bundle.get_execution_directory() / "Documenti.DefXml",
                when=Validator("files.input.easyfatt", eq=""),
                cast=lambda value: Path(
                    bundle.get_execution_directory() / "Documenti.DefXml"
                )
                if str(value).strip() == ""
                else Path(value),
            ),
            Validator(
                "files.input.addition",
                default=None,
                when=Validator("files.input.addition", eq=""),
                cast=lambda value: None if str(value).strip() == "" else Path(value),
            ),
            Validator(
                "files.output.csv",
                default=bundle.get_execution_directory() / "Documenti.csv",
                when=Validator("files.output.csv", eq=""),
                cast=lambda value: Path(
                    bundle.get_execution_directory() / "Documenti.csv"
                )
                if str(value).strip() == ""
                else Path(value),
            ),
            Validator(
                "files.output.kml",
                default=bundle.get_execution_directory() / "output.kml",
                when=Validator("files.output.kml", eq=""),
                cast=lambda value: Path(bundle.get_execution_directory() / "output.kml")
                if str(value).strip() == ""
                else Path(value),
            ),
            Validator(
                "easyfatt.customers.custom_field",
                default=1,
                when=Validator("easyfatt.customers.custom_field", eq=""),
                cast=lambda value: 1
                if str(value).strip() == ""
                else int(value),
            ),
            Validator(
                "features.kml_generation.google_api_key",
                default=None,
                when=Validator("features.kml_generation.google_api_key", eq=""),
                cast=lambda value: None
                if str(value).strip() == ""
                else str(value),
            ),
            Validator(
                "features.kml_generation.placemark_title",
                default="{customerName} ({customerCode}) {notes}",
                when=Validator("features.kml_generation.placemark_title", eq=""),
                cast=lambda value: "{customerName} ({customerCode}) {notes}"
                if str(value).strip() == ""
                else value,
            ),
        ],
        envvar_prefix="VERYEASYFATT",  # Prefix used by Dynaconf to load values from environment variables
    )


settings: SettingsSchema = _get_settings()  # pyright: ignore[reportGeneralTypeIssues]

# Setup default values for missing settings
# if str(settings.files.output.kml).strip() == "":
#     settings.files.output.kml = bundle.get_execution_directory() / "output.kml"
# settings.features.kml_generation.google_api_key
