from pathlib import Path
from typing import Any
import toml

import bundle

import logging
logger = logging.getLogger("danea-easyfatt.config")


CONFIG_FILENAME = "veryeasyfatt.config.toml"


def deepmerge(source, destination):
    """ Deep merge a dictionary.
    
    ! Bug if in A a given element contains a dict and in B any other type
	Source: https://stackoverflow.com/a/20666342/8965861
	"""
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            deepmerge(value, node)
        else:
            destination[key] = value

    return destination


def get_configuration(custom_config_file: (str | Path | None) = None) -> dict[str, Any]:
	""" Reads the user configuration file (if present) and merges it with the default configuration

	Args:
		custom_config_file (str | Path | None, optional): Path to a custom configuration file (passed via `-c`). Defaults to None.

	Raises:
		Exception: _description_

	Returns:
		configuration (dict[str, Any]): The final configuration
	"""
	default_config_file = bundle.get_root_directory()      / CONFIG_FILENAME
	user_config_file    = bundle.get_execution_directory() / CONFIG_FILENAME

	if custom_config_file is not None:
		user_config_file = Path(custom_config_file).resolve()

	default_configuration = {}
	user_configuration = {}
	
	if not default_config_file.exists():
		# Se non è stato compilato (quindi durante lo sviluppo) la configurazione DEVE esistere
		raise Exception(f"Impossibile trovare file di configurazione '{default_config_file}'. Solo la versione compilata può essere utilizzata senza configurazione.")
		
	
	default_configuration = toml.load(default_config_file)
	logger.debug(f"Configurazione default: {default_configuration}")
	
	if user_config_file.exists():
		logger.info(f"Trovato file di configurazione utente")
		user_configuration = toml.load(user_config_file)
		logger.debug(f"Configurazione utente: {user_configuration}")
	else:
		logger.warning(f"File di configurazione utente '{user_config_file}' non trovato.")
		logger.info(f"Utilizzo la configurazione di default")

	# Unisci le configurazioni
	# configuration = {**default_configuration, **user_configuration}
	return deepmerge(user_configuration, default_configuration)
