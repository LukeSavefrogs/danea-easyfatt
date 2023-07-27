from pathlib import Path
import xmltodict
import re

from app.clienti import get_intervallo_spedizioni, routexl_time_boundaries

import logging
logger = logging.getLogger("danea-easyfatt.csv")


def genera_csv (
        xml_text: str, 
        template_riga: str, 
        default_shipping_interval: str, 
        customer_files: list | str, 
        extra_field_id=1,
        extra_field_orario=4
    ):
    logger.debug(f"Trasformo l'XML in un dizionario")

    default_time_boundary = routexl_time_boundaries(default_shipping_interval)
    
    # Trasformo il CSV in un dizionario, in modo da poterlo traversare facilmente.
    xml_dict = xmltodict.parse(
        xml_input=xml_text
    )

    intervallo_spedizioni = {}
    
    lista_file_clienti = customer_files if isinstance(customer_files, list) else [customer_files]
    logger.debug(f"Inizio ricerca file '{'|'.join(lista_file_clienti)}'")
    
    # Restituisci l'intervallo spedizioni trovato nel primo dei file cercati.
    for file in lista_file_clienti:
        file_clienti = Path(file).resolve().absolute()
        if file_clienti.exists():
            logger.info(f"Trovato file '{file_clienti}'")
            logger.info(f"Gestione automatica degli orari di consegna abilitata.")
            intervallo_spedizioni = get_intervallo_spedizioni(filename=file_clienti, extra_field_id=extra_field_id)
            break
    else:
        logger.error(f"Nessun file trovato che corrisponda al pattern '{'|'.join(lista_file_clienti)}'")
        logger.warning(f"Gestione automatica degli orari di consegna disabilitata.")

    logger.debug(f"Intervallo spedizioni:\n {intervallo_spedizioni}")

    csv_lines = []
    for document in xml_dict["EasyfattDocuments"]["Documents"]["Document"]:
        indirizzo_spedizione = document["DeliveryAddress"] if document.get("DeliveryAddress", None) else document["CustomerAddress"]
        cap_spedizione = document["DeliveryPostcode"] if document.get("DeliveryAddress", None) else document["CustomerPostcode"]
        citta_spedizione = document["DeliveryCity"] if document.get("DeliveryAddress", None) else document["CustomerCity"]

        if document.get("TransportedWeight", None) is not None:
            weight_matched = re.search(pattern=r"([0-9,.]+)", string=document.get("TransportedWeight"))
            peso = weight_matched.group(0) if weight_matched is not None else 0
        else:
            peso = 0
        
        # Orari di spedizione (il minore sovrascrive il maggiore):
        # 1. Singolo ordine
        # 2. Profilo clienti
        # 3. Default
        #
        orario_spedizione_ordine = document.get(f"CustomField{extra_field_orario}", "")
        try:
            orario_spedizione = routexl_time_boundaries(orario_spedizione_ordine)
        except ValueError:
            orario_spedizione = None
        
        if orario_spedizione is not None:
            logger.info(f"Preso orario spedizione da ordine singolo: {orario_spedizione}")
        else:
            orario_spedizione = intervallo_spedizioni.get(document["CustomerCode"], None)
            if orario_spedizione is not None:
                logger.debug("Preso orario spedizione da profilo cliente")
            else:
                orario_spedizione = default_time_boundary
                logger.debug("Preso orario spedizione da valore di default")
        
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