from collections import defaultdict
import datetime
import logging
from pathlib import Path

import pydantic

import kmlb
from easyfatt_db_connector import EasyfattFDB, read_xml

from easyfatt_db_connector.xml.document import Document

logger = logging.getLogger("danea-easyfatt.kml")


class HashableBaseModel(pydantic.BaseModel):
    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))


class CustomerAddress(HashableBaseModel):
    """Model for a customer address."""

    code: str = pydantic.Field(alias="CodAnagr", frozen=True)
    name: str = pydantic.Field(alias="Nome", frozen=True)
    address: str = pydantic.Field(alias="Indirizzo", frozen=True)
    postcode: str = pydantic.Field(alias="Cap", frozen=True)
    city: str = pydantic.Field(alias="Citta", frozen=True)
    province: str = pydantic.Field(alias="Prov", frozen=True)
    country: str = pydantic.Field(alias="Nazione", frozen=True)
    is_customer: bool = pydantic.Field(alias="IsCustomer", frozen=True)
    is_primary: bool = pydantic.Field()
    alias: str = pydantic.Field(alias="CodDest", default="", frozen=True)

    @pydantic.validator("address", "postcode", "city", "province", "country", pre=True)
    def replace_none(cls, value):
        return value if value is not None else ""


def generate_kml(
    xml_filename: (Path | str),
    database_path: (Path | str),
    output_filename: (Path | str) = "export.kml",
):
    """Generate a KML file from an XML file and a database file.

    Args:
        xml_filename (Path | str): Path to the XML file.
        database_path (Path | str): Path to the database file.
        output_filename (Path | str, optional): Path to the output KML file. Defaults to "export.kml".
    """
    logger.info("Start")
    logger.info(f"Database path: {database_path}")
    logger.info(f"XML path: {xml_filename}")

    database = EasyfattFDB(database_path, download_firebird=True)

    xml_object = read_xml(xml_filename)

    logger.info("Connecting to database...")
    with database.connect() as connection:
        logger.info("Connected to database")

        anagrafiche = [
            CustomerAddress(**item, is_primary=True)
            for item in connection.cursor()
            .execute(
                """
                    SELECT anag."CodAnagr", ANAG."Nome", ANAG."Indirizzo", ANAG."Cap", ANAG."Citta", ANAG."Prov", IIF(naz."NomeNazionePrint" IS NULL, 'Italia', naz."NomeNazionePrint") AS "Nazione", IIF(anag."Cliente" = 1, 1, 0) AS "IsCustomer"
                    FROM "TAnagrafica" AS anag
                    LEFT JOIN "TNazioni" naz ON ANAG."Nazione" = naz."NomeNazione";
                """
            )
            .fetchallmap()
        ]

        anagrafiche_indirizzi_extra = [
            CustomerAddress(**item, is_primary=False)
            for item in connection.cursor()
            .execute(
                """
                    SELECT anag."CodAnagr", td."Nome", td."Indirizzo", td."Cap", td."Citta", td."Prov", IIF(naz."NomeNazionePrint" IS NULL, 'Italia', naz."NomeNazionePrint") AS "Nazione", IIF(anag."Cliente" = 1, 1, 0) AS "IsCustomer", td."CodDest"
                    FROM "TAnagrafica" AS anag
                    RIGHT JOIN "TAnagraficaDest" td ON td."IDAnagr" = ANAG."IDAnagr"
                    LEFT JOIN "TNazioni" naz ON td."Nazione" = naz."NomeNazione";
                """
            )
            .fetchallmap()
        ]

    # Lista di indirizzi
    customer_locations = []
    supplier_locations = []

    # Elenco ordinato di tutte le anagrafiche (con indirizzi primari e secondari)
    anagrafiche = sorted(
        anagrafiche + anagrafiche_indirizzi_extra,
        key=lambda x: (x.code, not x.is_primary, x.alias),
    )

    total_documents_processed = 0
    customers_unknown_address = []
    xml_documents = [document for document in xml_object.documents]

    # Lista di documenti raggruppati per codice cliente.
    documents_by_customer: defaultdict[str, list[Document]] = defaultdict(list)
    for d in [
        {document.customer.code: document}
        for document in xml_object.documents
        if document.customer is not None
    ]:
        for key, value in sorted(d.items()):
            documents_by_customer[key].append(value)

    # TODO: Add the company address
    # if xml_object.company is not None:
    #     if None in [
    #         xml_object.company.address,
    #         xml_object.company.postcode,
    #         xml_object.company.city,
    #         xml_object.company.country,
    #     ]:
    #         logger.warning("Company address is not complete")
    #     else:
    #         customer_locations.append(
    #             kmlb.search_poi(
    #                 f"{xml_object.company.address} {xml_object.company.postcode}, {xml_object.company.city}, {xml_object.company.country}",
    #                 hidden=False,
    #                 name=f"{xml_object.company.name} (MY COMPANY)",
    #                 style_to_use="Company Home",
    #             )
    #         )
    #         logger.info("Added company address")
    # END TODO

    # TIPI DI INDIRIZZI POSSIBILI:
    #   - Fornitori (anagrafica.is_customer == False):
    #       - Indirizzi primari (anagrafica.is_primary == True)
    #       - Indirizzi secondari (anagrafica.is_primary == False)
    #
    #   - Clienti (anagrafica.is_customer == True):
    #       - Indirizzi primari (anagrafica.is_primary == True)
    #       - Indirizzi secondari (anagrafica.is_primary == False)
    #       - Indirizzi documento (da analizzare XML):
    #           - conosciuti (vedi primari o secondari)
    #           - sconosciuti (aggiungere)
    address_buffer = []
    for anagrafica in anagrafiche:
        if address_buffer and anagrafica.code != address_buffer[0]["id"]:
            customer_locations.extend([item["data"] for item in address_buffer])

            logger.info(
                f"Added {len(address_buffer)} buffered unknown addresses for customer {address_buffer[0]['id']}"
            )
            address_buffer.clear()
            logger.debug("Buffer cleared")

        # --------------- Fornitori ---------------
        if not anagrafica.is_customer:
            supplier_locations.append(
                kmlb.search_poi(
                    f"{anagrafica.address} {anagrafica.postcode}, {anagrafica.city}, {anagrafica.country}",
                    hidden=True,
                    name=f"{anagrafica.name}",
                    style_to_use="Suppliers",
                )
            )
            continue

        # --------------- Clienti ---------------

        # 1. Controlla se ci sono documenti nell'XML per questo cliente
        if anagrafica.code in documents_by_customer.keys():
            logger.info(
                f"Il cliente ha {len(documents_by_customer[anagrafica.code])} documenti nell'XML"
            )

            # 1a. Controlla se ci sono documenti con indirizzi sconosciuti
            known_addresses = [
                document
                for document in documents_by_customer[anagrafica.code]
                if (
                    (
                        document.delivery is not None
                        and (
                            document.delivery.address == anagrafica.address
                            and document.delivery.postcode == anagrafica.postcode
                            and document.delivery.city == anagrafica.city
                            and document.delivery.country == anagrafica.country
                        )
                    )
                    or (
                        document.customer is not None
                        and document.customer.address == anagrafica.address
                        and document.customer.postcode == anagrafica.postcode
                        and document.customer.city == anagrafica.city
                        and document.customer.country == anagrafica.country
                    )
                )
            ]
            unknown_addresses = set(
                tuple(documents_by_customer[anagrafica.code])
            ) - set(tuple(known_addresses))

            logger.info(
                f"Il cliente ha {len(documents_by_customer[anagrafica.code])} documenti nell'XML (di cui {len(unknown_addresses)} sconosciuti)"
            )

            if known_addresses:
                address = known_addresses[0]

                # NOTA: L'indirizzo di spedizione ha sempre la precedenza su quello del cliente
                if address.delivery.address != "":
                    address_string = f"{address.delivery.address} {address.delivery.postcode}, {address.delivery.city}, {address.delivery.country}"
                else:
                    address_string = f"{address.customer.address} {address.customer.postcode}, {address.customer.city}, {address.customer.country}"

                customer_locations.append(
                    kmlb.search_poi(
                        address_string,
                        hidden=False,
                        name=f"{anagrafica.name} ({anagrafica.code})",
                        style_to_use="Customers",
                    )
                )

                logger.info(
                    f"Added {len(known_addresses)} known addresses for customer {anagrafica.code} ({anagrafica.name})"
                )
                total_documents_processed += len(known_addresses)
            else:
                customer_locations.append(
                    kmlb.search_poi(
                        f"{anagrafica.address} {anagrafica.postcode}, {anagrafica.city}, {anagrafica.country}",
                        hidden=True,
                        name=f"{anagrafica.name} ({anagrafica.code})",
                        style_to_use="Customers",
                    )
                )

            # Se ci sono documenti con indirizzi sconosciuti
            if unknown_addresses:
                # Salta se sono già stati processati
                if anagrafica.code in customers_unknown_address:
                    continue

                logger.debug(
                    f"Customer {anagrafica.code} ({anagrafica.name}) has {len(unknown_addresses)}/{len(documents_by_customer[anagrafica.code])} unknown addresses"
                )
                customers_unknown_address.append(anagrafica.code)

                for unknown_address in unknown_addresses:
                    # NOTA: L'indirizzo di spedizione ha sempre la precedenza su quello del cliente
                    if unknown_address.delivery.address != "":
                        address_string = f"{unknown_address.delivery.address} {unknown_address.delivery.postcode}, {unknown_address.delivery.city}, {unknown_address.delivery.country}"
                    else:
                        address_string = f"{unknown_address.customer.address} {unknown_address.customer.postcode}, {unknown_address.customer.city}, {unknown_address.customer.country}"

                    address_buffer.append(
                        {
                            "id": unknown_address.customer.code,
                            "data": kmlb.search_poi(
                                address_string,
                                hidden=False,
                                name=f"{unknown_address.customer.name} ({unknown_address.customer.code}) - NUOVO!",
                                style_to_use="Customers",
                            ),
                        }
                    )
                else:
                    logger.debug(
                        f"Buffered {len(unknown_addresses)} unknown addresses for customer {anagrafica.code} ({anagrafica.name})"
                    )

                total_documents_processed += len(
                    documents_by_customer[anagrafica.code]
                ) - len(known_addresses)
            # endif

            del documents_by_customer[anagrafica.code]

        else:
            # 2. This customer has no documents
            logger.debug(
                f"Customer {anagrafica.code} ({anagrafica.name}) has NO documents"
            )
            logger.debug(
                f"Aggiungo cliente {anagrafica.code} ({anagrafica.name}) - {'PRIMARIO' if anagrafica.is_primary else 'SECONDARIO'}"
            )
            customer_locations.append(
                kmlb.search_poi(
                    f"{anagrafica.address} {anagrafica.postcode}, {anagrafica.city}, {anagrafica.country}",
                    hidden=True,
                    name=f"{anagrafica.name} ({anagrafica.code})",
                    style_to_use="Customers",
                )
            )

    if total_documents_processed != len(xml_documents):
        logger.warning(
            f"Documenti processati: {total_documents_processed}/{len(documents_by_customer.keys())}"
        )

        unknown_customer_documents = 0
        for code, documents in documents_by_customer.items():
            for document in documents:
                # NOTA: L'indirizzo di spedizione ha sempre la precedenza su quello del cliente
                if document.delivery.address != "":
                    address_string = f"{document.delivery.address} {document.delivery.postcode}, {document.delivery.city}, {document.delivery.country}"
                else:
                    address_string = f"{document.customer.address} {document.customer.postcode}, {document.customer.city}, {document.customer.country}"

                customer_locations.append(
                    kmlb.search_poi(
                        address_string,
                        hidden=False,
                        name=f"{document.customer.name} ({document.customer.code}) - CLIENTE NON CENSITO!",
                        style_to_use="Customers",
                    )
                )
                unknown_customer_documents += 1

            logger.info(
                f"Added {len(documents)} unknown addresses for unknown customer {documents[0].customer.code} ({documents[0].customer.name})"
            )

        logger.warning(f"Added a total of {unknown_customer_documents} unknown customers")


    kml = kmlb.kml(
        name="Estrazione clienti e fornitori",
        description=f"This KML was automatically generated by VeryEasyfatt at {datetime.datetime.now():%d-%m-%Y %H:%M:%S}.",
        collapsed=False,
        features=[
            kmlb.folder(
                "Clienti",
                description="Elenco completo delle anagrafiche clienti",
                loose_items=customer_locations,
                collapsed=True,
            ),
            kmlb.folder(
                "Fornitori",
                description="Elenco completo delle anagrafiche fornitori",
                loose_items=supplier_locations,
                collapsed=True,
            ),
        ],
        # Define styles (https://kml4earth.appspot.com/icons.html)
        styles=[
            kmlb.point_style(
                "Company Home",  # Point style name
                "https://maps.google.com/mapfiles/kml/shapes/ranger_station.png",  # Icon
                ("#77c8d1", 100),  # Icon color
                1.0,  # Icon scale
                ("#ffffff", 100),  # Label color
                1.0,  # Label size
            ),
            kmlb.point_style(
                "Customers",  # Point style name
                "https://maps.google.com/mapfiles/kml/shapes/truck.png",  # Icon
                ("#ff0000", 100),  # Icon color
                1.0,  # Icon scale
                ("#ffffff", 100),  # Label color
                1.0,  # Label size
            ),
            kmlb.point_style(
                "Suppliers",  # Point style name
                "https://maps.google.com/mapfiles/kml/shapes/euro.png",  # Icon
                ("#ffff00", 100),  # Icon color
                1.0,  # Icon scale
                ("#ffffff", 100),  # Label color
                1.0,  # Label size
            ),
        ],
    )

    with open(output_filename, "w") as file:
        file.write(kml)


if __name__ == "__main__":
    try:
        generate_kml(
            r"tests\data\OrdiniCliente.DefXml",
            r"C:\Users\lucas\Documents\Danea Easyfatt/Arredo Ufficio (LaSorgente).eft",
        )
    except Exception as e:
        logger.error("An error occurred")
        logger.exception(e)
    finally:
        input("Premi invio per uscire...")
