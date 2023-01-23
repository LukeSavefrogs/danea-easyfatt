from pathlib import Path
from src.process_xml import modifica_xml
from src.process_csv import genera_csv

import src.configuration as configuration
import updater

import webbrowser

from packaging.version import Version
from rich.logging import RichHandler
import logging

logger = logging.getLogger(__name__)
logger.addHandler(RichHandler(
	rich_tracebacks=True,
	omit_repeated_times=False,
	log_time_format="[%d-%m-%Y %H:%M:%S]"
))
logger.setLevel(logging.DEBUG)


# -----------------------------------------------------------
#                        Inizio codice                       
# -----------------------------------------------------------
def main():
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
			logger.info(f"You're already running the latest version.")
	except Exception as error:
		logger.exception("Errore in fase di controllo aggiornamenti")

		logger.fatal("Impossibile continuare. Assicurati di fare uno screenshot di questa schermata e condividerla con lo sviluppatore.")

		return False


	REQUIRED_FILES = [
		Path(configuration.XML_EASYFATT_FILE),
		Path(configuration.XML_ADDITIONAL_FILE)
	]
	missing_required_file = False
	for required_file in REQUIRED_FILES:
		if not required_file.resolve().exists():
			logger.critical(f"File richiesto '{required_file.resolve().absolute()}' non trovato.")
			missing_required_file = True
	
	if missing_required_file:
		return False


	# 1. Modifico l'XML
	nuovo_xml = ""
	righe_csv = ""

	try:
		# Aggiunge il contenuto di `additional_xml_file` all'interno di `easyfatt_xml`
		nuovo_xml = modifica_xml(
			easyfatt_xml_file = configuration.XML_EASYFATT_FILE,
			additional_xml_file = configuration.XML_ADDITIONAL_FILE
		)

		logger.info(f"Analisi e modifica XML terminata..")
	except Exception:
		logger.exception("Errore furante la modifica del file XML.")
		return False


	# 2. Genero il CSV sulla base del template
	try:
		righe_csv = genera_csv(
			xml_text=nuovo_xml,
			template_riga=configuration.TEMPLATE_STRING
		)
		
		# Salvo il csv su file
		with open(configuration.CSV_OUTPUT_FILE, "w") as json_file:
			json_file.write('\n'.join(righe_csv))

		logger.info(f"Creazione CSV '{configuration.CSV_OUTPUT_FILE}' terminata..")
	except Exception:
		logger.exception("Errore furante la generazione del file CSV.")
		return False

# Per compilare: pyinstaller --onefile --clean .\src\main.py
if __name__ == '__main__':
	try:
		main()
	except Exception as e:
		logger.exception("Eccezione inaspettata nella funzione main")
	finally:
		input("Premi [INVIO] per terminare il programma...")