from pathlib import Path
import xml.etree.ElementTree as ET
import xmltodict
import re

from clienti import get_intervallo_spedizioni

import logging
logger = logging.getLogger("danea-easyfatt.csv")


def genera_csv (xml_text, template_riga):
	# Trasformo il CSV in un dizionario, in modo da poterlo traversare facilmente.
	xml_dict = xmltodict.parse(
		xml_input=xml_text
	)

	intervallo_spedizioni = {}
	file_clienti = Path("./ExportClienti.xlsx").resolve().absolute()
	if file_clienti.exists():
		logger.info(f"Trovato file 'ExportClienti.xlsx'")
		logger.warning(f"Gestione automatica degli orari di consegna abilitata.")
		intervallo_spedizioni = get_intervallo_spedizioni(filename=file_clienti, extra_field_id=3)

	csv_lines = []
	for document in xml_dict["EasyfattDocuments"]["Documents"]["Document"]:
		indirizzo_spedizione = document["DeliveryAddress"] if document.get("DeliveryAddress", None) else document["CustomerAddress"]
		cap_spedizione = document["DeliveryPostcode"] if document.get("DeliveryAddress", None) else document["CustomerPostcode"]
		citta_spedizione = document["DeliveryCity"] if document.get("DeliveryAddress", None) else document["CustomerCity"]
		peso = re.search(pattern=r"([0-9,.]+)", string=document["TransportedWeight"]).group(0) if document.get("TransportedWeight", None) else 0


		csv_lines.append(template_riga.format(
			CustomerName = document["CustomerName"],
			CustomerCode = document["CustomerCode"],
			eval_IndirizzoSpedizione = indirizzo_spedizione,
			eval_CAPSpedizione = str(cap_spedizione),
			eval_CittaSpedizione = citta_spedizione,
			eval_intervalloSpedizione = intervallo_spedizioni.get(document["CustomerCode"], "7:00>>16:00"),
			eval_pesoSpedizione = str(peso)
		))
	
	return csv_lines

