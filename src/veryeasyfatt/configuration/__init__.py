from pathlib import Path
from dynaconf import Dynaconf, Validator

from veryeasyfatt import bundle
from veryeasyfatt.configuration.schemas import SettingsSchema


settings: SettingsSchema = Dynaconf(  # pyright: ignore[reportGeneralTypeIssues]
    settings_files=["veryeasyfatt.config.toml", ".secrets.toml"],
    merge_enabled=True,  # Merge all found files into one configuration.
    validate_on_update=False,  # Validate the configuration when it is updated.
    validators=[  # Custom validators.
        Validator(
            "easyfatt.database.filename",
            default="",
            cast=lambda value: Path(value).expanduser().resolve()
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
    ],
    envvar_prefix="VERYEASYFATT",  # Prefix used by Dynaconf to load values from environment variables
)

# Setup default values for missing settings
# if str(settings.files.output.kml).strip() == "":
#     settings.files.output.kml = bundle.get_execution_directory() / "output.kml"
# settings.features.kml_generation.google_api_key
