import json
import os
from pathlib import Path
from process_xml import modifica_xml
from process_csv import genera_csv

import updater

import webbrowser

from packaging.version import Version
from rich.logging import RichHandler
import logging

logger = logging.getLogger("danea-easyfatt")
logger.addHandler(RichHandler(
	rich_tracebacks=True,
	omit_repeated_times=False,
	log_time_format="[%d-%m-%Y %H:%M:%S]"
))
logger.setLevel(logging.DEBUG)

import pandas as pd
import pint

EASYFATT_DOCUMENT_DTYPE = {
	"CustomerCode": str,
	"CustomerPostcode": str,
	"CustomerVatCode": str,
	"CustomerTel": str,
}

import bundle
import toml

CONFIG_FILENAME = "veryeasyfatt.config.toml"

# -----------------------------------------------------------
#                        Inizio codice                       
# -----------------------------------------------------------
def main():
	logger.debug(f"Execution directory: '{bundle.get_execution_directory()}'")
	logger.debug(f"Bundle directory   : '{bundle.get_bundle_directory()}'")
	logger.debug(f"Root directory     : '{bundle.get_root_directory()}'")


	# ==================================================================
	#                       Controllo di versione
	# ==================================================================
	try:
		if updater.update_available():
			latest_release = updater.get_latest_version()
			latest_version = Version(latest_release['version'])
			current_version = Version(updater.get_current_version())

			logger.warning(f"An update is available (remote is '{latest_version}', while current is '{current_version}')")
			webbrowser.open(latest_release["url"], new=0, autoraise=True)
			
			return False
		else:
			logger.debug(f"La tua versione è aggiornata! :)")
	except Exception:
		logger.exception("Errore in fase di controllo aggiornamenti")

		logger.fatal("Impossibile continuare. Assicurati di fare uno screenshot di questa schermata e condividerla con lo sviluppatore.")

		return False


	# ==================================================================
	#                       Lettura configurazione
	# ==================================================================
	default_config_file = bundle.get_root_directory()      / CONFIG_FILENAME
	user_config_file    = bundle.get_execution_directory() / CONFIG_FILENAME
	
	default_configuration = {}
	user_configuration = {}
	
	if not default_config_file.exists():
		# Se non è stato compilato (quindi durante lo sviluppo) la configurazione DEVE esistere
		logger.critical(f"Impossibile trovare file di configurazione '{default_config_file}'. Solo la versione compilata può essere utilizzata senza configurazione.")
		return False
	
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
	configuration = deepmerge(user_configuration, default_configuration)

	if configuration["log_level"]:
		logger.setLevel(logging.getLevelName(configuration["log_level"]))

	logger.debug(f"Configurazione in uso: \n{json.dumps(configuration, indent=4)}")


	# ==================================================================
	#                     Controllo file richiesti
	# ==================================================================
	REQUIRED_FILES = [
		Path(configuration["files"]["input"]["easyfatt"]),
	]
	missing_required_file = False
	for required_file in REQUIRED_FILES:
		if not required_file.resolve().exists():
			logger.critical(f"File richiesto '{required_file.resolve().absolute()}' non trovato.")
			missing_required_file = True
	
	if missing_required_file:
		return False


	# 1. Modifico l'XML
	nuovo_xml: str
	if configuration["files"]["input"]["addition"] != "":
		try:
			# Aggiunge il contenuto di `additional_xml_file` all'interno di `easyfatt_xml`
			nuovo_xml = modifica_xml(
				easyfatt_xml_file   = Path(configuration["files"]["input"]["easyfatt"]).resolve(),
				additional_xml_file = Path(configuration["files"]["input"]["addition"]).resolve(),
			)

			logger.info(f"Analisi e modifica XML terminata..")
		except Exception as e:
			logger.exception(f"Errore furante la modifica del file XML: {repr(e)}")
			return False
	else:
		nuovo_xml = Path(configuration["files"]["input"]["easyfatt"]).resolve().read_text()


	# 2. Genero il CSV sulla base del template
	try:
		righe_csv = genera_csv(
			xml_text = nuovo_xml,
			template_riga = configuration["options"]["output"]["csv_template"],
			customer_files = configuration["easyfatt"]["customers"]["export_filename"],
			extra_field_id = configuration["easyfatt"]["customers"]["custom_field"],
			default_shipping_interval = configuration["features"]["shipping"]["default_interval"]
		)
		
		# Salvo il csv su file
		with open(configuration["files"]["output"]["csv"], "w") as csv_file:
			csv_file.write('\n'.join(righe_csv))

		logger.info(f"Creazione CSV '{configuration['files']['output']['csv']}' terminata..")
	except Exception:
		logger.exception("Errore furante la generazione del file CSV.")
		return False



	# 3. Calcolo il peso totale della spedizione
	try:
		ureg = pint.UnitRegistry(autoconvert_offset_to_baseunit=True)
		ureg.default_format = "~P"

		df = pd.read_xml(nuovo_xml, parser='etree', xpath='./Documents/Document', dtype=EASYFATT_DOCUMENT_DTYPE)

		# Effettuo una prima pulizia dei valori a solo scopo di visualizzazione.
		#
		# IMPORTANTE: Per evitare valori sballati nel totale sono costretto a
		#             trasformare il separatore decimale nel formato inglese (.)
		df["TransportedWeight"] = df["TransportedWeight"].map(
			lambda v: ureg.Quantity(str(v).replace(".", "").replace(",", ".").lower()) if v is not None else v
		)

		pd.set_option('display.max_columns', None)
		pd.set_option('display.max_rows', None)
		logger.debug(f"Effettuata prima analisi del peso trasportato: \n{df.get(['CustomerCode', 'TransportedWeight'])}")
		pd.reset_option('display.max_columns')
		pd.reset_option('display.max_rows')

		df["TransportedWeight"] = df["TransportedWeight"].map(
			lambda v: ureg.Quantity(str(v).lower()).to("g").magnitude if v is not None else v
		)
		logger.debug(f"Effettuata conversione in grammi: \n{df.get(['CustomerCode', 'TransportedWeight'])}")

		peso_totale = ureg.Quantity(df["TransportedWeight"].sum(), 'g') 
		logger.info(f"Peso totale calcolato: {peso_totale.to('kg')} ({peso_totale.to('t')})")
	
	except Exception as e:
		logger.error(f"Errore in fase di calcolo peso totale: {repr(e)}")
		logger.exception("Errore in fase di calcolo peso totale")


	logger.info("Procedura terminata.")


	# ==================================================================
	#                     Apro file CSV generato
	# ==================================================================
	# Issue #20
	print("\n")
	if input(f"Aprire il file '{configuration['files']['output']['csv']}'? [Si/No] ").lower() in ["y", "yes", "s", "si"]:
		os.startfile(Path(configuration['files']['output']['csv']).resolve(), 'open')
	print("\n")


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



# Per compilare: pyinstaller --onefile --clean .\src\main.py
if __name__ == '__main__':
	try:
		main()
	except Exception as e:
		logger.exception("Eccezione inaspettata nella funzione main")
	finally:
		input("Premi [INVIO] per terminare il programma...")
		pass