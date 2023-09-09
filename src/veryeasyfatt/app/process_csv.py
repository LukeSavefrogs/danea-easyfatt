from io import StringIO
from pathlib import Path
import pandas as pd
import re
import logging

from veryeasyfatt.app.clienti import get_intervallo_spedizioni, routexl_time_boundaries
from veryeasyfatt.formatter import SimpleFormatter
from veryeasyfatt.configuration import settings

logger = logging.getLogger("danea-easyfatt.csv")
logger.addHandler(logging.NullHandler())

EASYFATT_DOCUMENT_DTYPE = {
    "CustomerCode": str,
    "CustomerPostcode": str,
    "DeliveryPostcode": str,
    "CustomerVatCode": str,
    "CustomerTel": str,
}


def genera_csv(
    xml_text: str,
    extra_field_orario=4,
):
    lista_file_clienti = settings.easyfatt.customers.export_filename

    logger.debug(f"Trasformo l'XML in un dizionario")
    safe_formatter = SimpleFormatter()

    default_time_boundary = routexl_time_boundaries(
        settings.features.shipping.default_interval
    )

    # Trasformo il CSV in un dizionario, in modo da poterlo traversare facilmente.
    intervallo_spedizioni = {}

    logger.debug(f"Inizio ricerca file '{'|'.join(map(str, lista_file_clienti))}'")

    # Restituisci l'intervallo spedizioni trovato nel primo dei file cercati.
    for file in lista_file_clienti:
        file_clienti = Path(file).resolve().absolute()
        if file_clienti.exists():
            logger.info(f"Trovato file '{file_clienti}'")
            logger.info(f"Gestione automatica degli orari di consegna abilitata.")
            intervallo_spedizioni = get_intervallo_spedizioni(
                filename=file_clienti,
                extra_field_id=settings.easyfatt.customers.custom_field,
            )
            break
    else:
        logger.error(
            f"Nessun file trovato che corrisponda al pattern '{'|'.join(map(str, lista_file_clienti))}'"
        )
        logger.warning(f"Gestione automatica degli orari di consegna disabilitata.")

    logger.debug(f"Intervallo spedizioni:\n {intervallo_spedizioni}")

    df = pd.read_xml(
        StringIO(xml_text),
        parser="etree",
        xpath="./Documents/Document",
        dtype=EASYFATT_DOCUMENT_DTYPE,  # type: ignore
    )
    df = df.reset_index()  # make sure indexes pair with number of rows

    # TODO: Do not use `iterrows` since it could become very slow with large datasets (see https://stackoverflow.com/a/55557758/8965861).
    csv_lines = []
    for index, document in df.iterrows():
        indirizzo_spedizione = (
            document["DeliveryAddress"]
            if document.get("DeliveryAddress", None)
            else document["CustomerAddress"]
        )
        cap_spedizione = (
            document["DeliveryPostcode"]
            if document.get("DeliveryAddress", None)
            else document["CustomerPostcode"]
        )
        citta_spedizione = (
            document["DeliveryCity"]
            if document.get("DeliveryAddress", None)
            else document["CustomerCity"]
        )

        if document.get("TransportedWeight", None) is not None:
            weight_matched = re.search(
                pattern=r"([0-9,.]+)", string=str(document.get("TransportedWeight", ""))
            )
            peso = weight_matched.group(0) if weight_matched is not None else 0
        else:
            peso = 0

        # Orari di spedizione (il minore sovrascrive il maggiore):
        # 1. Singolo ordine
        # 2. Profilo clienti
        # 3. Default
        #
        orario_spedizione_ordine = str(
            document.get(f"CustomField{extra_field_orario}", "")
        )
        try:
            orario_spedizione = routexl_time_boundaries(orario_spedizione_ordine)
        except ValueError:
            orario_spedizione = None

        if orario_spedizione is not None:
            logger.info(
                f"Preso orario spedizione da ordine singolo: {orario_spedizione}"
            )
        else:
            orario_spedizione = intervallo_spedizioni.get(
                document["CustomerCode"], None
            )
            if orario_spedizione is not None:
                logger.debug("Preso orario spedizione da profilo cliente")
            else:
                orario_spedizione = default_time_boundary
                logger.debug("Preso orario spedizione da valore di default")

        logger.debug(
            f"Orario di spedizione per il cliente '{document['CustomerCode']}': {orario_spedizione}"
        )

        csv_lines.append(
            safe_formatter.format(
                settings.options.output.csv_template,
                CustomerName=document["CustomerName"],
                CustomerCode=document["CustomerCode"],
                eval_IndirizzoSpedizione=indirizzo_spedizione,
                eval_CAPSpedizione=str(cap_spedizione),
                eval_CittaSpedizione=citta_spedizione,
                eval_intervalloSpedizione=orario_spedizione,
                eval_pesoSpedizione=str(peso),
            )
        )

    return csv_lines
