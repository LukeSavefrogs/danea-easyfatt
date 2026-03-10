import enum

from pydantic.dataclasses import dataclass

from veryeasyfatt.app.integrations.routexl.timing import RouteXLTimeBoundary

class StringTemplateComponents(enum.Enum):
    """ Identifies the accepted components for string templates used in formatting imported data for RouteXL. """
    NAME = "name"
    SERVICE_TIME = "service_time"
    TIME_BOUNDARY = "time_boundary"
    COMMENT = "comment"
    CAPACITY = "capacity"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}.{self.name}>"

    def format(self, value: str) -> str:
        if self == StringTemplateComponents.NAME:
            return f"@{value}@"
        elif self == StringTemplateComponents.SERVICE_TIME:
            return f"({value})"
        elif self == StringTemplateComponents.TIME_BOUNDARY:
            return f"{value}"
        elif self == StringTemplateComponents.COMMENT:
            return "{" + value + "}"
        elif self == StringTemplateComponents.CAPACITY:
            return f"^{value}^"
        else:
            raise ValueError(f"Unsupported component type: {self}")

@dataclass
class StringTemplate:
    """ Represents a template for formatting imported data into a specific string format for RouteXL.
    The template consists of a list of components (defined in StringTemplateComponents) and a separator
    that is used to join the formatted components together.
    
    Example usage:
    >>> template = StringTemplate(
    ...     components=[
    ...         StringTemplateComponents.NAME,
    ...         StringTemplateComponents.SERVICE_TIME,
    ...         StringTemplateComponents.TIME_BOUNDARY,
    ...         StringTemplateComponents.COMMENT,
    ...         StringTemplateComponents.CAPACITY,
    ...     ],
    ...     separator=" "
    ... )
    None
    >>> template.format({
    ...     StringTemplateComponents.NAME: "Stop 1",
    ...     StringTemplateComponents.SERVICE_TIME: "30",
    ...     StringTemplateComponents.TIME_BOUNDARY: "08:00>>16:00",
    ...     StringTemplateComponents.COMMENT: "This is a comment.",
    ...     StringTemplateComponents.CAPACITY: "10",
    ... })
    '@Stop 1@ (30) 08:00>>16:00 {This is a comment.} ^10^'
    """
    components: list[StringTemplateComponents]
    separator: str = " "

    def __init__(self, components: list[StringTemplateComponents], separator=" "):
        self.components = components
        self.separator = separator

    def __str__(self):
        return self.__class__.__name__ + "(" + ", ".join(repr(comp) for comp in self.components) + ")"
    
    def format(self, values: dict[StringTemplateComponents, str]) -> str:
        formatted_values = [comp.format(values[comp]) for comp in self.components]
        return self.separator.join(formatted_values)
    
@dataclass
class ImportedRecord:
    """ Represents a single record of imported data with fields for name, service time, time boundary, comment, and capacity. """
    name: str
    """ Name of the stop. """

    service_time: int
    """ Service times in minutes. """
    
    time_boundary: str
    """ Time boundary for the stop. """
    
    comment: str
    """ Comment for the stop. """
    
    capacity: int
    """ Demand for capacity at the stop. """

@dataclass
class ImportedData:
    records: list[ImportedRecord]

    template: StringTemplate = StringTemplate(
        components=[
            StringTemplateComponents.NAME,
            StringTemplateComponents.SERVICE_TIME,
            StringTemplateComponents.TIME_BOUNDARY,
            StringTemplateComponents.COMMENT,
            StringTemplateComponents.CAPACITY,
        ],
        separator=" "
    )

    def add_record(self, record: ImportedRecord):
        self.records.append(record)

    def to_routexl_format(self, template: StringTemplate | None = None):
        """Convert the imported records to a format suitable for RouteXL.
        
        - Names between `@` and `@`
        - Service times in minutes between `(` and `)`
        - Ready and/or due time as hh:mm (24hr) before and after `>>`
        - Comments between `{` and `}`
        - Demand for capacity as number between `^` and `^`
        - Heading (angle of approach) in degrees between `*` and `*`
        """
        if template is None:
            template = self.template
        
        converted_records = []
        for record in self.records:
            time_boundary = RouteXLTimeBoundary.from_string(record.time_boundary)
            converted_record = template.format({
                StringTemplateComponents.NAME: record.name,
                StringTemplateComponents.SERVICE_TIME: str(record.service_time),
                StringTemplateComponents.TIME_BOUNDARY: str(time_boundary),
                StringTemplateComponents.COMMENT: record.comment,
                StringTemplateComponents.CAPACITY: str(record.capacity),
            })

            converted_records.append(converted_record)
        return '\n'.join(converted_records)
    
if __name__ == "__main__":
    from rich.table import Table
    from rich.console import Console

    console = Console()

    record = ImportedRecord(
        name="Stop 1",
        service_time=30,
        time_boundary="08:00 a 16:00",
        comment="This is a comment.",
        capacity=10
    )
    imported_data = ImportedData(records=[record])

    imported_data.add_record(
        ImportedRecord(
            name="Stop 2",
            service_time=45,
            time_boundary="09:00 > 17:00",
            comment="Another comment.",
            capacity=20
        )
    )

    table = Table(title="Imported Data", show_lines=True)
    table.add_column("Label", style="cyan", no_wrap=True)
    table.add_column("Value", style="yellow")

    table.add_row("Template", str(imported_data.template))
    table.add_row("Imported data", repr(imported_data))
    table.add_row("Records", "\n".join(f"{record}" for record in imported_data.records))
    table.add_row("RouteXL Template (default)", imported_data.to_routexl_format())
    table.add_row("RouteXL Template (custom)", imported_data.to_routexl_format(StringTemplate(
        components=[
            StringTemplateComponents.COMMENT,
            StringTemplateComponents.NAME,
            StringTemplateComponents.SERVICE_TIME,
            StringTemplateComponents.TIME_BOUNDARY,
            StringTemplateComponents.CAPACITY,
        ],
        separator=" | "
    )))

    
    console.print(table)