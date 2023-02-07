from pathlib import Path
import xml.etree.ElementTree as ET
import xmltodict
import re

from clienti import get_intervallo_spedizioni

import logging
logger = logging.getLogger("danea-easyfatt.csv")


def genera_csv (xml_text: str, template_riga: str, customer_excel=None, extra_field_id=1):
	logger.debug(f"Trasformo l'XML in un dizionario")
	# Trasformo il CSV in un dizionario, in modo da poterlo traversare facilmente.
	xml_dict = xmltodict.parse(
		xml_input=xml_text
	)

	intervallo_spedizioni = {}
	if customer_excel is not None:
		logger.debug(f"Passato nome file excel: '{customer_excel}'")
		file_clienti = Path(customer_excel).resolve().absolute()
		if file_clienti.exists():
			logger.info(f"Trovato file '{file_clienti}'")
			logger.warning(f"Gestione automatica degli orari di consegna abilitata.")
			intervallo_spedizioni = get_intervallo_spedizioni(filename=file_clienti, extra_field_id=extra_field_id)

	else:
		logger.debug(f"Nessun excel specificato. Inizio ricerca file.")
		for ext in ["xlsx", "ods"]:
			file_clienti = Path(f"./Soggetti.{ext}").resolve().absolute()
			if file_clienti.exists():
				logger.info(f"Trovato file 'Soggetti.{ext}'")
				logger.warning(f"Gestione automatica degli orari di consegna abilitata.")
				intervallo_spedizioni = get_intervallo_spedizioni(filename=file_clienti, extra_field_id=extra_field_id)
				break
	
	logger.debug(f"Intervallo spedizioni:\n {intervallo_spedizioni}")

	csv_lines = []
	for document in xml_dict["EasyfattDocuments"]["Documents"]["Document"]:
		indirizzo_spedizione = document["DeliveryAddress"] if document.get("DeliveryAddress", None) else document["CustomerAddress"]
		cap_spedizione = document["DeliveryPostcode"] if document.get("DeliveryAddress", None) else document["CustomerPostcode"]
		citta_spedizione = document["DeliveryCity"] if document.get("DeliveryAddress", None) else document["CustomerCity"]
		peso = re.search(pattern=r"([0-9,.]+)", string=document["TransportedWeight"]).group(0) if document.get("TransportedWeight", None) else 0

		orario_spedizione = intervallo_spedizioni.get(document["CustomerCode"], "7:00>>16:00")
		logger.debug(f"Orario di spedizione per il cliente '{document['CustomerCode']}': {orario_spedizione}")
		
		csv_lines.append(template_riga.format(
			CustomerName = document["CustomerName"],
			CustomerCode = document["CustomerCode"],
			eval_IndirizzoSpedizione = indirizzo_spedizione,
			eval_CAPSpedizione = str(cap_spedizione),
			eval_CittaSpedizione = citta_spedizione,
			eval_intervalloSpedizione = orario_spedizione,
			eval_pesoSpedizione = str(peso)
		))
	
	return csv_lines