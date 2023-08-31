import logging
import types
from typing import Any as _Any, Literal as _Literal, Union as _Union
from pathlib import Path as _Path
import datetime as _datetime

import pickle as _pickle
import json as _json

logger = logging.getLogger("danea-easyfatt.caching")

def persist_to_file(
    file_name: _Union[str, _Path],
    backend: _Literal["json", "pickle"] = "pickle",
    include=[],
    enabled: bool|str =True,
):
    """Decorator that caches the result of a function to a file.

    Source: https://stackoverflow.com/a/16464555/8965861

    Args:
        file_name (str): The name of the file where to store the cache.
    """
    cache_backend: types.ModuleType
    read_mode: _Literal["r", "rb"]
    write_mode: _Literal["w", "wb"]

    if backend == "pickle":
        cache_backend = _pickle
        read_mode = "rb"
        write_mode = "wb"
    elif backend == "json":
        cache_backend = _json
        read_mode = "r"
        write_mode = "w"
    else:
        raise ValueError(f"Invalid backend: {backend}")

    def decorator(original_func):
        cache = {
            "data": {},
            "metadata": {
                "version": "1",
                "date": _datetime.datetime.now(),
            },
        }

        try:
            with open(file_name, read_mode) as f:
                cache = cache_backend.load(f)
        except (IOError, ValueError):
            pass

        def new_func(*args, **kwargs):
            nonlocal enabled

            cache_enabled = True
            if type(enabled) == str:
                cache_enabled = kwargs.get(enabled, True)
                cache_enabled = cache_enabled if type(cache_enabled) == bool else True
            elif type(enabled) == bool:
                cache_enabled = enabled

            key = args + tuple(kwargs.values())
            if include:
                key = tuple(
                    [
                        args[arg]
                        for arg in include
                        if type(arg) == int and arg < len(args)
                    ]
                    + [
                        kwargs[arg]
                        for arg in include
                        if type(arg) == str and arg in kwargs
                    ]
                )

            if key not in cache["data"].keys():
                logger.debug(f"Cache miss for '{key}'")
                cache["data"][key] = original_func(*args, **kwargs)

                if cache_enabled:
                    with open(file_name, write_mode) as f:
                        cache_backend.dump(cache, f)
                else:
                    logger.debug(f"Cache disabled for key '{key}'")
            else:
                logger.debug(f"Cache hit for '{key}'")

            return cache["data"][key]

        return new_func

    return decorator
