from typing import Any, Literal, Union
from pathlib import Path
import datetime

import pickle
import json

def persist_to_file(file_name: Union[str, Path], backend: Literal['json', 'pickle'] = 'pickle'):
    """ Decorator that caches the result of a function to a file.
    
    Source: https://stackoverflow.com/a/16464555/8965861

    Args:
        file_name (str): The name of the file where to store the cache.
    """
    if backend == 'pickle':
        cache_backend = pickle
        read_mode = 'rb'
        write_mode = 'wb'
    elif backend == 'json':
        cache_backend = json
        read_mode = 'r'
        write_mode = 'w'
    else:
        raise ValueError(f"Invalid backend: {backend}")
    
    def decorator(original_func):
        cache: dict[Any, Any] = {
            'data': {},
            'metadata': {
                'version': '1',
                'date': datetime.datetime.now(),
            }
        }

        try:
            with open(file_name, read_mode) as f:
                cache = cache_backend.load(f)
        except (IOError, ValueError):
            print(f"Cache file '{file_name}' not found. Creating new one.")
            pass

        def new_func(param):
            if param not in cache['data']:
                print(f"Cache miss for '{param}'")
                cache['data'][param] = original_func(param)

                with open(file_name, write_mode) as f:
                    cache_backend.dump(cache, f)
            else:
                print(f"Cache hit for '{param}'")
            return cache['data'][param]

        return new_func

    return decorator
