""" Entry point of the application. """
import json
import os
from pathlib import Path
from app.process_xml import modifica_xml
from app.process_csv import genera_csv

import app.config_manager as configuration_manager

import logging

logger = logging.getLogger("danea-easyfatt.application.core")

import pandas as pd
import pint

EASYFATT_DOCUMENT_DTYPE = {
	"CustomerCode": str,
	"CustomerPostcode": str,
	"CustomerVatCode": str,
	"CustomerTel": str,
}


# -----------------------------------------------------------
#                        Inizio codice                       
# -----------------------------------------------------------
def main(configuration_file = None):
	# ==================================================================
	#                       Lettura configurazione
	# ==================================================================
	try:
		configuration = configuration_manager.get_configuration(configuration_file)
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
			logger.exception(f"Errore durante la modifica del file XML: {repr(e)}")
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
		logger.exception("Errore durante la generazione del file CSV.")
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