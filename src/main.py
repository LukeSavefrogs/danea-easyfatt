import json
import os
from pathlib import Path
import sys
from process_xml import modifica_xml
from process_csv import genera_csv

import config_manager as configuration_manager


import updater

import webbrowser

import argparse


from packaging.version import Version
from rich.logging import RichHandler
import logging

default_handler = logging.StreamHandler(sys.stdout)
default_handler.setFormatter(logging.Formatter(fmt="[%(asctime)s] %(levelname)-8s %(message)s", datefmt="%d-%m-%Y %H:%M:%S"))

logger = logging.getLogger("danea-easyfatt")
logger.addHandler(default_handler)
logger.setLevel(logging.DEBUG)

# The Rich handler will be used if `--disable-rich-handler` is not passed
rich_handler = RichHandler(
	rich_tracebacks=True,
	omit_repeated_times=False,
	log_time_format="[%d-%m-%Y %H:%M:%S]"
)

import pandas as pd
import pint

EASYFATT_DOCUMENT_DTYPE = {
	"CustomerCode": str,
	"CustomerPostcode": str,
	"CustomerVatCode": str,
	"CustomerTel": str,
}

import bundle

# Windows specific definitions
if sys.platform != 'win32':
	logger.critical("This program is available only for the Windows platform.")
	sys.exit(1)


# -----------------------------------------------------------
#                        Inizio codice                       
# -----------------------------------------------------------
def main():
	logger.debug(f"Execution directory: '{bundle.get_execution_directory()}'")
	logger.debug(f"Bundle directory   : '{bundle.get_bundle_directory()}'")
	logger.debug(f"Root directory     : '{bundle.get_root_directory()}'")


	# ==================================================================
	#                     Parametri linea di comando
	# ==================================================================
	parser = argparse.ArgumentParser(
		description='Easyfatt made even easier.',
		add_help=True,
	)
	parser.add_argument(
		"-c", "--config",
		required=False,
		help="Specify a custom TOML configuration file.",
		dest="configuration_file",
		metavar="FILENAME",
		type=str
	)
	parser.add_argument(
		"-V", "--version",
		help="Show the current version and exit.",
		action='version',
		version=f"v{updater.get_current_version()}",
	)
	parser.add_argument(
		"--disable-version-check",
		help="Disable the version check process.",
		dest="enable_version_check",
		action="store_false",
		default=True,
	)
	parser.add_argument(
		"--disable-rich-logging",
		help="Disable the Rich logging handler (used for testing).",
		dest="enable_rich_logging",
		action="store_false",
		default=True,
	)
	cli_args = parser.parse_args()

	logger.debug(f"CLI parameters: {cli_args}")

	if cli_args.enable_rich_logging:
		logger.removeHandler(default_handler)
		logger.addHandler(rich_handler)



	# ==================================================================
	#                       Controllo di versione
	# ==================================================================
	if not cli_args.enable_version_check:
		logger.warning("Il controllo versione è stato disattivato tramite CLI (--disable-version-check).")
	else:
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
	try:
		configuration = configuration_manager.get_configuration(cli_args.configuration_file)
	except Exception as e:
		logger.critical(f"Errore in fase di recupero configurazione: {e}")
		return False
	
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
		ureg = pint.UnitRegistry(autoconvert_offset_to_baseunit=True, on_redefinition="raise")
		ureg.default_format = "~P"
		ureg.define('quintal = 100 * kg = q = centner')

		df = pd.read_xml(
			nuovo_xml,
			parser='etree',
			xpath='./Documents/Document',
			dtype=EASYFATT_DOCUMENT_DTYPE # type: ignore
		)

		# Effettuo una prima pulizia dei valori a solo scopo di visualizzazione.
		#
		# IMPORTANTE: Per evitare valori sballati nel totale sono costretto a
		#             trasformare il separatore decimale nel formato inglese (.)
		df["TransportedWeight"] = df["TransportedWeight"].map(
			lambda v: ureg.Quantity(str(v).replace(".", "").replace(",", ".").lower()) if v is not None else v
		)

		# Converto in grammi
		df["TransportedWeight"] = df["TransportedWeight"].map(
			lambda v: ureg.Quantity(str(v).lower()).to("g").magnitude if v is not None else v
		)

		peso_totale = ureg.Quantity(df["TransportedWeight"].sum(), 'g') 
		logger.info(f"Peso totale calcolato: {peso_totale.to('kg')} ({peso_totale.to('q')} / {peso_totale.to('t')})")
	
	except Exception as e:
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




# Per compilare: pyinstaller --onefile --clean .\src\main.py
if __name__ == '__main__':
	try:
		main()
	except Exception as e:
		logger.exception("Eccezione inaspettata nella funzione main")
	finally:
		input("Premi [INVIO] per terminare il programma...")
		pass