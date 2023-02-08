from pathlib import Path
from typing import Any, Union
import pandas as pd
import numpy as np

from rich.logging import RichHandler
import logging

import re

import hashlib
import pickle
import bundle

logger = logging.getLogger("danea-easyfatt.clienti")



CACHE_FILENAME = "customer_info.pickle"

def rename_extra_field(column_name):
	"""Rinomina il campo 'Extra {N}' in 'IntervalloSpedizione'. Lascia inalterati i nomi delle altre colonne.

	Args:
		column_name (str): Nome della colonna corrente

	Returns:
		str: Nuovo nome della colonna
	"""
	return "IntervalloSpedizione" if re.match(r"^Extra [0-9]+$", column_name) else column_name



def formatta_orario(value):
	"""Formatta l'orario nel formato HH:mm (aggiungendo '0*' e ':00' dove necessario)

	Args:
		value (str): L'orario da formattare

	Returns:
		str: Orario formattato nel formato HH:mm
	"""
	orario = value.split(":")

	if len(orario) < 2:
		orario.append("0")

	return ':'.join(map(lambda s: s.strip().zfill(2), orario))

def routexl_time_boundaries(string: str):
	"""Generates a valid "Ready and due time" string to be used for csv import

	See also:
		https://docs.routexl.com/index.php?title=Import#Additional_fields:~:text=Ready%20and%20due%20time%20as%20hh%3Amm%20before%20and%20after%20%3E%3E

	Args:
		string (str): The string to convert

	Raises:
		ValueError: If the input value is not a string

	Returns:
		str | None: The time boundaries in the form "HH:MM>>HH:MM"
	"""
	REGEX_INTERVALLO = r'([0-9:]+)\s*(?:>+|-+|\s+a\s+)\s*([0-9:]+)'

	if not isinstance(string, str):
		raise ValueError("Input string must be of type 'str'")

	if not re.match(REGEX_INTERVALLO, string):
		return None

	return '>>'.join(
		map(formatta_orario, 
			re.match(REGEX_INTERVALLO, string).groups()
		)
	)

def get_customers_data(filename: Union[str, Path], cache: bool=True, cache_path: Union[str, Path, None] = None) -> list[dict[str, Any]]:
	"""Ricava i dati cliente dal file Excel/Libreoffice esportato da Easyfatt.

	- Se `cache=True` allora viene salvata una copia dei dati recuperati dal file su
	un file. In questo modo l'esecuzione successiva sarà molto più veloce in quanto 
	non dovrà ricaricare il file Excel ma solo leggere il file `.pickle`.

	Args:
		`filename` (str | pathlib.Path): Percorso al file Excel/Libreoffice da analizzare
		`cache` (bool, optional): Se usare la cache. Defaults to True.
		`cache_path` (str | pathlib.Path, optional): Percorso alla cartella contenente il file di cache. Defaults to None.

	Returns:
		list: Una lista di dizionari (convertibile a dataframe semplicemente passandolo come parametro) contenente tutte le voci del foglio excel.
	"""
	md5sum = ""

	if not cache:
		logger.warning("Cache bypassata forzatamente.")
		
	else:
		try:
			with open(filename, "rb") as f:
				md5sum = hashlib.md5(f.read()).hexdigest()
			
			logger.info(f"Hash md5 file excel: '{md5sum}'")

			cache_dir = cache_path if cache_path else bundle.get_execution_directory() / ".cache"
			cache_file = cache_dir / CACHE_FILENAME

			# Creo il percorso se non esiste già
			Path(cache_dir).mkdir(parents=True, exist_ok=True)

			logger.debug(f"Cerco file di cache '{cache_file}'")
			if cache_file.exists():
				logger.debug(f"Trovato file cache '{cache_file}'") 
				
				cached_data = {}
				with open(cache_file, "rb") as pickle_file:
					cached_data = pickle.load(pickle_file)

				cached_metadata = cached_data.get('metadata')
				last_update: pd.Timestamp = cached_metadata.get('date', None)

				logger.debug(f"Ultima elaborazione effettuata il {last_update.strftime('%d-%m-%Y %H:%M:%S') if last_update else 'NO-DATA'}")
				logger.debug(f"Hash md5 pickle: '{cached_metadata.get('hash', None)}'")
				if cached_metadata.get('hash', None) == md5sum:
					logger.info(f"Carico i dati dal file di cache.")
					return cached_data["data"]

				logger.debug(f"File di cache invalidato. Necessaria rielaborazione dati.") 
		except Exception as err:
			logger.error(f"Errore in fase di recupero cache ({repr(err)}). Proseguo normalmente")

	logger.debug(f"Carico file '{filename}'")

	# Legge sia file `*.xlsx` che `*.ods`
	df = pd.read_excel(filename, dtype=str)

	logger.info(f"File excel caricato (trovate {df.shape[0]} righe e {df.shape[1]} colonne)")
	
	df_dict = df.to_dict('records')
	if cache:
		return_data = {
			"metadata": {
				"date": pd.Timestamp.now(),
				"hash": md5sum
			},
			"data": df_dict
		}

		with open(cache_file, "wb") as pickle_file:
			pickle.dump(return_data.copy(), pickle_file)

		logger.info(f"Salvato file di cache '{cache_file}'. La prossima esecuzione dovrebbe essere più veloce.")

	return df_dict


def get_intervallo_spedizioni(filename: Union[str, Path], extra_field_id=1):
	customer_data = get_customers_data(filename)
	df = pd.DataFrame(customer_data)
	logger.info(f"File excel caricato (trovate {df.shape[0]} righe e {df.shape[1]} colonne)")

	df = df.replace(r'^\s*$', np.nan, regex=True)
	
	cod_not_present = df[df["Cod."].isnull()]
	if not cod_not_present.empty:
		not_present_info = cod_not_present.get(['Denominazione', 'Partita Iva', 'Indirizzo', 'Cap', 'Città', 'Prov.'])
		logger.error(f"Trovati i seguenti clienti con campo 'Cod.' NON VALORIZZATO:\n{not_present_info}")
		return False

	customer_info: pd.DataFrame = df.get(['Cod.', f'Extra {extra_field_id}'])
	logger.info(f"Trovate informazioni cliente: \n{customer_info}")
	
	customer_info = customer_info.rename(mapper=rename_extra_field, axis='columns')
	logger.debug(f"Rinominata colonna 'Extra {extra_field_id}' in 'IntervalloSpedizione'")
	
	customer_info = customer_info.replace({ np.nan: None })

	# Supporto le seguenti sintassi:
	#     - '08 > 16' (con o senza spazi)
	#     - '8 >> 16' (con o senza spazi)
	#     - '08 - 16' (con o senza spazi)
	#     - '08 a 16'
	# 
	# Normalizzo inoltre tutti gli intervalli in modo da avere l'orario SEMPRE preceduto da uno '0'.
	# Esempio: 
	# 	'08' invece di '8'
	customer_info['IntervalloSpedizione'] = [
		routexl_time_boundaries(value.strip()) if (value is not None) else None
		for value in customer_info['IntervalloSpedizione']
	]
	logger.info(f"Sanificati valori della colonna 'IntervalloSpedizione'")

	logger.info(f"Informazioni cliente finali: \n{customer_info}")

	return { 
		customer["Cod."]: customer["IntervalloSpedizione"]
		for customer in customer_info.to_dict('records')
		if customer["IntervalloSpedizione"] is not None
	}


if __name__ == '__main__':
	logger.addHandler(RichHandler(
		rich_tracebacks=True,
		omit_repeated_times=False,
		log_time_format="[%d-%m-%Y %H:%M:%S]"
	))
	logger.setLevel(logging.DEBUG)

	customers = get_customers_data('tests/data/ExportClienti.xlsx', cache=True)

	customers = get_intervallo_spedizioni('tests/data/ExportClienti.xlsx')

	logger.info(f"Recuperata lista clienti: {customers}")