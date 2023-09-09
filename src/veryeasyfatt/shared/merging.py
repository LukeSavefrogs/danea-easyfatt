from typing import overload
from functools import reduce
from collections.abc import MutableMapping


@overload
def deepmerge(source: dict, destination: dict, /) -> dict:
    """Updates two dicts of dicts recursively.

    If either mapping has leaves that are non-dicts, the
    leaves of the second dictionary overwrite the ones
    from the first.

    Args:
        source (dict): The source dictionary.
        destination (dict): The destination dictionary.
    """
    ...


@overload
def deepmerge(*dicts) -> dict:
    """Updates multiple dicts of dicts recursively.

    Args:
        *dicts (dict): The dictionaries to merge.
    """
    ...


def deepmerge(*dicts) -> dict:
    def _deepmerge(source: dict, destination: dict) -> dict:
        """Updates two dicts of dicts recursively (https://stackoverflow.com/a/24088493/8965861)."""
        for k, v in source.items():
            if k in destination:
                # this next check is the only difference!
                if all(isinstance(e, MutableMapping) for e in (v, destination[k])):
                    destination[k] = deepmerge(v, destination[k])
                # we could further check types and merge as appropriate here.
        d3 = source.copy()
        d3.update(destination)
        return d3

    return reduce(_deepmerge, tuple(dicts))
