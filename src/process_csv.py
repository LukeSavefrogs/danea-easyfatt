import xml.etree.ElementTree as ET
import xmltodict
import re

import logging
logger = logging.getLogger(__name__)




def genera_csv (xml_text, template_riga):
	# Trasformo il CSV in un dizionario, in modo da poterlo traversare facilmente.
	xml_dict = xmltodict.parse(
		xml_input=xml_text
	)

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
			eval_pesoSpedizione = str(peso)
		))
	
	return csv_lines


# Foglio `fromDaneaToRouteXL`:
#		 =CONCAT(
#		 	"@";
#		 	'Danea-destinazioni'!B2;	# -----> =Danea!C2 & " " & Danea!A2
#		   "@";
#		   'Danea-destinazioni'!C2;	# -----> =SE(Danea!$N2="";Danea!D2;Danea!N2)
#		   " ";
#		   'Danea-destinazioni'!D2;	# -----> =SE(Danea!$N2="";Danea!E2;Danea!O2)
#		   " ";
#		   'Danea-destinazioni'!E2;	# -----> =SE(Danea!$N2="";Danea!F2;Danea!P2)
#		   "(20)";
#		   "7:00>>16:00";
#		   "^";
#		   SE(
#		 		LUNGHEZZA('Danea-destinazioni'!V2)>3;
#		   	SINISTRA(
#		 			'Danea-destinazioni'!V2;
#			   		( LUNGHEZZA('Danea-destinazioni'!V2)-3 )
#			 	);
#		   	0
#		 	);
#		   "^"
#		 )