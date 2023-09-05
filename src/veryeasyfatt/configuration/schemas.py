import dataclasses
from pathlib import Path

from dynaconf import Dynaconf


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
    addition: Path


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
    filename: Path


@dataclasses.dataclass
class CustomersEasyfattSchema:
    custom_field: Path
    export_filename: Path


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
    google_api_key: str
    placemark_title: str
