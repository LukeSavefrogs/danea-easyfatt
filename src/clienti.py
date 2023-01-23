import json
import pandas as pd
import numpy as np

from rich.logging import RichHandler
import logging

import re

logger = logging.getLogger(__name__)
logger.addHandler(RichHandler(
	rich_tracebacks=True,
	omit_repeated_times=False,
	log_time_format="[%d-%m-%Y %H:%M:%S]"
))
logger.setLevel(logging.INFO)


CUSTOMER_EXTRA_FIELD = 3
REGEX_INTERVALLO = r'([0-9:]+)\s*(?:>+|-+|\s+a\s+)\s*([0-9:]+)'

def rename_extra_field(column_name):
	"""Rinomina il campo 'Extra {N}' in 'IntervalloSpedizione'. Lascia inalterati i nomi delle altre colonne.

	Args:
		column_name (str): Nome della colonna corrente

	Returns:
		str: Nuovo nome della colonna
	"""
	return "IntervalloSpedizione" if re.match("^Extra [0-9]+$", column_name) else column_name


def sanitize_extra_field(value):
	if re.match(r'([0-9]+)(>+|-+|\s+|\s+a\s+)([0-9]+)', value):
		return re.sub(r'([0-9]+)(>+|-+|\s+|\s+a\s+)([0-9]+)', repl='\1 >> \3', string=value) 
	return None


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
	return { 
		customer["Cod."]: customer["IntervalloSpedizione"]
		for customer in customer_info.to_dict('records')
		if customer["IntervalloSpedizione"] is not None
	}

if __name__ == '__main__':
	customers = get_intervallo_spedizioni('src/ExportClienti.xlsx', extra_field_id=CUSTOMER_EXTRA_FIELD)

	logger.info(f"Recuperata lista clienti: {customers}")