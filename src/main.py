from src.process_xml import modifica_xml
from src.process_csv import genera_csv

from rich.logging import RichHandler
import logging

import src.configurazione as configurazione

logger = logging.getLogger()
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
	nuovo_xml = ""
	righe_csv = ""


	# 1. Modifico l'XML
	try:
		# Aggiunge il contenuto di `additional_xml_file` all'interno di `easyfatt_xml`
		nuovo_xml = modifica_xml(
			easyfatt_xml_file = configurazione.XML_EASYFATT_FILE,
			additional_xml_file = configurazione.XML_ADDITIONAL_FILE
		)

		logger.info(f"Analisi e modifica XML terminata..")
	except Exception as e:
		logger.exception("Errore furante la modifica del file XML.")
		return False


	# 2. Genero il CSV sulla base del template
	try:
		righe_csv = genera_csv(
			xml_text=nuovo_xml,
			template_riga=configurazione.TEMPLATE_STRING
		)
		
		# Salvo il csv su file
		with open(configurazione.CSV_OUTPUT_FILE, "w") as json_file:
			json_file.write('\n'.join(righe_csv))

		logger.info(f"Creazione CSV '{configurazione.CSV_OUTPUT_FILE}' terminata..")
	except Exception as e:
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