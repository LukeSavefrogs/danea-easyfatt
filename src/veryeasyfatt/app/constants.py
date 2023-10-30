from enum import Enum

class SuperEnum(Enum):
    """ Source: https://stackoverflow.com/a/76867417/8965861. """
    @classmethod
    def to_dict(cls):
        """Returns a dictionary representation of the enum."""
        return {e.name: e.value for e in cls}

    @classmethod
    def items(cls):
        """Returns a list of all the enum items."""
        return [(e.name, e.value) for e in cls]

    @classmethod
    def keys(cls):
        """Returns a list of all the enum keys."""
        return [e.name for e in cls]
    
    @classmethod
    def values(cls):
        """Returns a list of all the enum values."""
        return [e.value for e in cls]


class ApplicationGoals(SuperEnum):
    CSV_GENERATOR = "csv-generator"
    KML_GENERATOR = "kml-generator"
    INITIALIZE_GEO_CACHE = "initialize-geo-cache"
    INITIALIZE_GEO_CACHE_DRYRUN = "initialize-geo-cache-dryrun"
