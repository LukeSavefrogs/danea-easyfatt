import xml.etree.ElementTree as ET
from pathlib import Path
import logging

from veryeasyfatt.configuration import settings

logger = logging.getLogger("danea-easyfatt.xml")
logger.addHandler(logging.NullHandler())


def is_valid_xml(value):
    """Checks if the provided string is a valid XML.

    Args:
            value (str): XML string

    Returns:
            bool: `True` if the string is a valid XML text, `False` otherwise.
    """
    try:
        ET.fromstring(value)
    except ET.ParseError:
        return False
    return True


def modifica_xml() -> str:
    """Aggiunge il contenuto di `additional_xml_file` all'interno di `easyfatt_xml`

    Returns:
        xml_text (str): Il testo XML modificato.
    """
    easyfatt_xml_file = settings.files.input.easyfatt
    additional_xml_file = settings.files.input.addition

    if additional_xml_file is None:
        raise ValueError("Il file da aggiungere non è stato specificato")

    logger.debug(
        f'File XML generato dal gestionale Danea Easyfatt: "{easyfatt_xml_file}"'
    )
    logger.debug(f'File XML contenente il testo da inserire: "{additional_xml_file}"')

    additional_xml_content = ""
    with open(additional_xml_file, "r", encoding="utf-8") as file:
        additional_xml_content = file.read()

    if not is_valid_xml(additional_xml_content):
        raise Exception(f"Il file '{additional_xml_file}' non contiene un XML valido")

    tree = ET.parse(easyfatt_xml_file)

    elementi_documents_trovati = tree.getroot().findall("./Documents")
    if len(elementi_documents_trovati) != 1:
        logger.error(
            f"Il file '{additional_xml_file}' non contiene un tag 'Documents' valido."
        )
        logger.error(
            f"Mi aspettavo di trovare 1 solo tag 'Documents' (trovati: {len(elementi_documents_trovati)})"
        )
        raise Exception(
            f"Il file '{additional_xml_file}' non contiene un tag 'Documents' valido."
        )

    # Elemento 'Documents' contenente tutti i tag 'Document'
    elemento_documents = elementi_documents_trovati[0]

    totale_documents_prima = len(elemento_documents.findall("Document"))
    logger.debug(f"Trovati {totale_documents_prima} tag 'Document'")

    logger.info(f"Aggiungo il contenuto del file '{additional_xml_file}'")
    elemento_documents.insert(0, ET.fromstring(additional_xml_content))

    totale_documents_dopo = len(elemento_documents.findall("Document"))

    if totale_documents_dopo <= totale_documents_prima:
        raise ValueError("Non è stato aggiunto nessun tag 'Documenti'")

    logger.debug(f"Trovati {totale_documents_dopo} tag 'Document'")

    return ET.tostring(
        tree.getroot(),
        encoding="UTF-8",
        xml_declaration=True,
        short_empty_elements=False,
    )
