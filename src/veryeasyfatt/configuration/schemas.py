import dataclasses
from pathlib import Path
from typing import Literal as _Literal

from veryeasyfatt.configuration.dynaconf_merge import Dynaconf


@dataclasses.dataclass
class SettingsSchema(Dynaconf):
    files: "FilesSchema"
    easyfatt: "EasyfattSchema"
    options: "OptionsSchema"
    features: "FeaturesSchema"
    log_level: str = "INFO"


@dataclasses.dataclass
class FilesSchema:
    input: "InputFilesSchema"
    output: "OutputFilesSchema"


@dataclasses.dataclass
class InputFilesSchema:
    easyfatt: Path
    addition: Path | None


@dataclasses.dataclass
class OutputFilesSchema:
    kml: Path
    csv: Path


@dataclasses.dataclass
class EasyfattSchema:
    database: "DatabaseEasyfattSchema"
    customers: "CustomersEasyfattSchema"


@dataclasses.dataclass
class DatabaseEasyfattSchema:
    filename: Path | None


@dataclasses.dataclass
class CustomersEasyfattSchema:
    custom_field: int
    export_filename: list[Path]


@dataclasses.dataclass
class OptionsSchema:
    output: "OutputOptionsSchema"


@dataclasses.dataclass
class OutputOptionsSchema:
    csv_template: str


@dataclasses.dataclass
class FeaturesSchema:
    shipping: "ShippingFeaturesSchema"
    kml_generation: "KmlGenerationFeaturesSchema"


@dataclasses.dataclass
class ShippingFeaturesSchema:
    default_interval: str


@dataclasses.dataclass
class KmlGenerationFeaturesSchema:
    google_api_key: str | None
    placemark_title: str
    location_search_type: _Literal["strict", "postcode"]
