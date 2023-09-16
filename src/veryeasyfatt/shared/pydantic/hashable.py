import pydantic


class HashableBaseModel(pydantic.BaseModel):
    """Base class for hashable pydantic models."""

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))
