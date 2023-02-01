import json
from pathlib import Path
import pandas as pd
import numpy as np

from rich.logging import RichHandler
import logging

import re

import hashlib
import pickle
import bundle

logger = logging.getLogger("danea-easyfatt.clienti")


CUSTOMER_EXTRA_FIELD = 3
REGEX_INTERVALLO = r'([0-9:]+)\s*(?:>+|-+|\s+a\s+)\s*([0-9:]+)'

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



def get_intervallo_spedizioni(filename, extra_field_id=1):
	md5sum = ""
	with open(filename, "rb") as f:
		md5sum = hashlib.md5(f.read()).hexdigest()
	
	logger.info(f"Hash md5 file excel: '{md5sum}'")

	cache_dir = bundle.get_execution_directory() / ".cache"
	cache_file = cache_dir / CACHE_FILENAME

	# Creo il percorso se non esiste già
	Path(cache_dir).mkdir(parents=True, exist_ok=True)

	logger.debug(f"Cerco file di cache '{cache_file}'")
	if cache_file.exists():
		logger.debug(f"Trovato file cache '{cache_file}'") 
		with open(cache_file, "rb") as pickle_file:
			cached_data = pickle.load(pickle_file)
		
		logger.debug(f"Hash md5 pickle: '{cached_data.get('metadata', {}).get('hash', None)}'")
		if cached_data and cached_data.get('metadata', {}).get('hash', None) == md5sum:
			logger.info(f"Carico i dati dal file di cache.") 
			return cached_data["data"]

		logger.debug(f"File di cache invalidato. Necessaria rielaborazione dati.") 

 
	logger.debug(f"Carico file '{filename}'")
	df = pd.read_excel(filename, dtype=str)
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
	logger.info(f"Rinominata colonna 'Extra {extra_field_id}' in 'IntervalloSpedizione'")
	
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
		'>>'.join(
			map(formatta_orario, 
				re.match(REGEX_INTERVALLO, string=value.strip()).groups()
			)
		)
		if value is not None and re.match(REGEX_INTERVALLO, value.strip())
		else None
		for value in customer_info['IntervalloSpedizione']
	]
	logger.info(f"Sanificati valori della colonna 'IntervalloSpedizione'")

	logger.info(f"Informazioni cliente finali: \n{customer_info}")
	return_data = {
		"metadata": {
			"hash": md5sum
		},
		"data": { 
			customer["Cod."]: customer["IntervalloSpedizione"]
			for customer in customer_info.to_dict('records')
			if customer["IntervalloSpedizione"] is not None
		}
	}

	with open(cache_file, "wb") as pickle_file:
		pickle.dump(return_data.copy(), file=pickle_file)
	logger.info(f"Salvato file di cache '{cache_file}'. La prossima esecuzione dovrebbe essere più veloce.")

	return return_data["data"]


if __name__ == '__main__':
	customers = get_intervallo_spedizioni('src/ExportClienti.xlsx', extra_field_id=CUSTOMER_EXTRA_FIELD)

	logger.info(f"Recuperata lista clienti: {customers}")