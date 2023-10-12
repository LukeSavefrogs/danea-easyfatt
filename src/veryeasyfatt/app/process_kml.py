import datetime
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any, Union

import pydantic

import kmlb
import xml.etree.ElementTree as ET

import geopy.geocoders
import geopy.location
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders.base import Geocoder

from easyfatt_db_connector import EasyfattFDB, read_xml
from easyfatt_db_connector.xml.document import Document

from veryeasyfatt.app import caching
import veryeasyfatt.bundle as bundle
from veryeasyfatt.shared.formatter import SimpleFormatter
from veryeasyfatt.configuration import settings
from veryeasyfatt.shared.pydantic.hashable import HashableBaseModel

logger = logging.getLogger("danea-easyfatt.kml")
logger.addHandler(logging.NullHandler())


class CustomerAddress(HashableBaseModel):
    """Model for a customer address."""

    code: str = pydantic.Field(alias="CodAnagr", frozen=True)
    name: str = pydantic.Field(alias="Nome", frozen=True)
    address: str = pydantic.Field(alias="Indirizzo", frozen=True)
    postcode: str = pydantic.Field(alias="Cap", frozen=True)
    city: str = pydantic.Field(alias="Citta", frozen=True)
    province: str = pydantic.Field(alias="Prov", frozen=True)
    country: str = pydantic.Field(alias="Nazione", frozen=True)
    alias: str = pydantic.Field(alias="CodDest", default="", frozen=True)
    fiscal_code: str = pydantic.Field(alias="CodiceFiscale", default="", frozen=True)
    vat_code: str = pydantic.Field(alias="PartitaIva", default="", frozen=True)
    homepage: str = pydantic.Field(alias="HomePage", default="", frozen=True)

    is_customer: bool = pydantic.Field(alias="IsCustomer", frozen=True)
    is_supplier: bool = pydantic.Field(alias="IsSupplier", frozen=True)
    is_primary: bool = pydantic.Field()

    @pydantic.validator(
        "address",
        "postcode",
        "city",
        "province",
        "country",
        "vat_code",
        "fiscal_code",
        "homepage",
        pre=True,
    )
    def replace_none(cls, value):
        return value if value is not None else ""


@caching.persist_to_file(
    file_name=(bundle.get_execution_directory() / ".cache" / "locations.pickle"),
    backend="pickle",
    include=[
        "address",
        0,
    ],  # Include the first positional argument or the keyword argument 'address'
    enabled="cache",
)
def search_location(
    address: str, google_api_key: str | None = None, geocoder=None, **kwargs
) -> geopy.location.Location:
    """Search for a location.

    Args:
        address (str): Address to search.
        google_api_key (str, optional): Google API key. Defaults to None.
        geocoder (Geocoder, optional): Geocoder to use. Defaults to None.
        cache (bool, optional): Whether to cache the result or not. Defaults to True.

    Returns:
        geopy.location.Location: Location object.

    Raises:
        Exception: If no geocoder is passed as argument and no Google API key is provided.
        Exception: If the location is not found.
    """
    if geocoder is None:
        if google_api_key is None or google_api_key.strip() == "":
            raise Exception(
                "Google API key MUST be provided if no geocoder is passed as argument."
            )

        geolocator = geopy.geocoders.GoogleV3(api_key=google_api_key)
        geocoder = RateLimiter(
            geolocator.geocode,
            min_delay_seconds=1 / 5,  # Max 5 requests per second
            swallow_exceptions=False,
        )

    location: Union[geopy.location.Location, None] = geocoder(
        address.title(),
        language="it",
        exactly_one=False,
    )  # pyright: ignore[reportGeneralTypeIssues]

    if location is None or (isinstance(location, list) and len(location) == 0):
        raise Exception(f"Location '{address.title()}' not found")
    
    _location_separator = '\n → '
    if len(location) > 1:
        raise Exception(f"Multiple locations found for '{address}':{_location_separator}{_location_separator.join([str(l) for l in location])}")

    return location[0]


def get_coordinates(
    address: str, google_api_key: str, caching=True
) -> tuple[float, float, float]:
    """Get the coordinates of an address.

    Args:
        address (str): Address to search.

    Returns:
        tuple[float, float]: Tuple containing the latitude and longitude of the address.
    """
    logger.debug(f"Searching for '{address}'")
    location = search_location(address, google_api_key, cache=caching)
    logger.debug(f"Found location: {location}")
    
    return (location.longitude, location.latitude, location.altitude)


class Placemark(object):
    def __init__(
        self, name, coordinates, address="", description="", hidden=False, style=None
    ) -> None:
        self.name = name
        self.coordinates = coordinates
        self.address = address
        self.description = description
        self.hidden = hidden
        self.style = style

    def __str__(self) -> str:
        attributes = [
            f"{key}={value}"
            for key, value in self.__dict__.items()
            if not key.startswith("_")
        ]
        return f"Placemark({', '.join(attributes)})"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Placemark):
            return False

        return self.name == o.name and self.coordinates == o.coordinates

    def __hash__(self) -> int:
        return hash((self.name, self.coordinates))

    # Define dunder methods that will be used to enable sorting on a list of Placemark objects
    def __lt__(self, o: object) -> bool:
        if not isinstance(o, Placemark):
            return False

        return self.name < o.name

    def __le__(self, o: object) -> bool:
        if not isinstance(o, Placemark):
            return False

        return self.name <= o.name

    def __gt__(self, o: object) -> bool:
        if not isinstance(o, Placemark):
            return False

        return self.name > o.name

    def __ge__(self, o: object) -> bool:
        if not isinstance(o, Placemark):
            return False

        return self.name >= o.name

    def to_kml(self) -> ET.Element:
        """Transforms the object into a KML string.

        Returns:
            ET.Element: KML element.
        """
        placemark: ET.Element = kmlb.point(
            name=self.name,
            coords=self.coordinates,
            hidden=self.hidden,
            style_to_use=self.style,
        )

        description_el = placemark.find("description")
        if description_el is not None:
            description_el.text = self.description

        return placemark


def generate_kml() -> str:
    """Generate a KML string from an XML file and a database file."""
    google_api_key = settings.features.kml_generation.google_api_key
    if google_api_key is None or google_api_key.strip() == "":
        raise Exception(
            "Google API key not found in the configuration file. Cannot continue."
        )

    placemark_title = settings.features.kml_generation.placemark_title
    database_path = settings.easyfatt.database.filename

    if database_path is None:
        raise Exception(
            "Database path not found in the configuration file. Cannot continue."
        )

    safe_formatter = SimpleFormatter()

    logger.info(f"Database path: {database_path}")
    logger.info(f"XML path: '{settings.files.input.easyfatt}'")

    xml_object = read_xml(settings.files.input.easyfatt, convert_types=True)
    anagrafiche = get_all_addresses(database_path)

    populate_cache(google_api_key, addresses=anagrafiche)

    # Lista di indirizzi
    customer_locations: list[Placemark] = []
    supplier_locations: list[Placemark] = []

    total_documents_processed = 0
    customers_unknown_address = []

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
    address_buffer: list[dict[str, Any]] = []
    for anagrafica in anagrafiche:
        logger.debug(
            f"Anagrafica in corso: {anagrafica.code} ({anagrafica.name}) [{'cliente' if anagrafica.is_customer else 'fornitore'}]"
        )

        if address_buffer and anagrafica.code != address_buffer[0]["id"]:
            customer_locations.extend([item["data"] for item in address_buffer])

            logger.info(
                f"Added {len(address_buffer)} buffered unknown addresses for customer {address_buffer[0]['id']}"
            )
            address_buffer.clear()
            logger.debug("Buffer cleared")

        # Un'anagrafica può essere sia cliente che fornitore
        # --------------- Fornitori ---------------
        if anagrafica.is_supplier:
            supplier_locations.append(
                Placemark(
                    name=safe_formatter.format(
                        placemark_title,
                        customerName=anagrafica.name,
                        customerCode=anagrafica.code,
                        customerFiscalCode=anagrafica.fiscal_code,
                        customerVatCode=anagrafica.vat_code,
                        customerHomepage=anagrafica.homepage,
                        notes="",
                    ),
                    coordinates=get_coordinates(
                        f"{anagrafica.address} {anagrafica.postcode}, {anagrafica.city}, {anagrafica.country}",
                        google_api_key,
                    ),
                    hidden=True,
                    style="Suppliers",
                )
            )

        # Un'anagrafica può essere sia cliente che fornitore
        # --------------- Clienti ---------------
        if anagrafica.is_customer:
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
                                document.delivery.address.lower()
                                == anagrafica.address.lower()
                                and document.delivery.postcode.lower()
                                == anagrafica.postcode.lower()
                                and document.delivery.city.lower()
                                == anagrafica.city.lower()
                                and document.delivery.country.lower()
                                == anagrafica.country.lower()
                            )
                        )
                        or (
                            document.customer is not None
                            and document.customer.address.lower()
                            == anagrafica.address.lower()
                            and document.customer.postcode.lower()
                            == anagrafica.postcode.lower()
                            and document.customer.city.lower()
                            == anagrafica.city.lower()
                            and document.customer.country.lower()
                            == anagrafica.country.lower()
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
                        Placemark(
                            name=safe_formatter.format(
                                placemark_title,
                                customerName=anagrafica.name,
                                customerCode=anagrafica.code,
                                customerFiscalCode=anagrafica.fiscal_code,
                                customerVatCode=anagrafica.vat_code,
                                customerHomepage=anagrafica.homepage,
                                notes="",
                            ),
                            coordinates=get_coordinates(address_string, google_api_key),
                            hidden=False,
                            style="Customers",
                        )
                    )

                    logger.info(
                        f"Added {len(known_addresses)} known addresses for customer {anagrafica.code} ({anagrafica.name})"
                    )
                    total_documents_processed += len(known_addresses)

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
                                "data": Placemark(
                                    name=safe_formatter.format(
                                        placemark_title,
                                        customerName=unknown_address.customer.name,
                                        customerCode=unknown_address.customer.code,
                                        customerFiscalCode=unknown_address.customer.fiscal_code,
                                        customerVatCode=unknown_address.customer.vat_code,
                                        customerHomepage=anagrafica.homepage,
                                        notes="- NUOVO!",
                                    ),
                                    coordinates=get_coordinates(
                                        address_string, google_api_key
                                    ),
                                    hidden=False,
                                    style="Customers",
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
            # endif

            else:
                # 2. This customer has no documents
                logger.debug(
                    f"Customer {anagrafica.code} ({anagrafica.name}) has NO documents"
                )
                logger.debug(
                    f"Aggiungo cliente {anagrafica.code} ({anagrafica.name}) - {'PRIMARIO' if anagrafica.is_primary else 'SECONDARIO'}"
                )
                customer_locations.append(
                    Placemark(
                        name=safe_formatter.format(
                            placemark_title,
                            customerName=anagrafica.name,
                            customerCode=anagrafica.code,
                            customerFiscalCode=anagrafica.fiscal_code,
                            customerVatCode=anagrafica.vat_code,
                            customerHomepage=anagrafica.homepage,
                            notes="",
                        ),
                        coordinates=get_coordinates(
                            f"{anagrafica.address} {anagrafica.postcode}, {anagrafica.city}, {anagrafica.country}",
                            google_api_key,
                        ),
                        hidden=True,
                        style="Customers",
                    )
                )

    else:
        # Clear the buffer if there are still addresses in it
        if address_buffer:
            customer_locations.extend([item["data"] for item in address_buffer])

            logger.info(
                f"Added {len(address_buffer)} buffered unknown addresses for customer {address_buffer[0]['id']}"
            )
            address_buffer.clear()
            logger.debug("Buffer cleared")

    if total_documents_processed != len(xml_object.documents):
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
                    Placemark(
                        name=safe_formatter.format(
                            placemark_title,
                            customerName=document.customer.name,
                            customerCode=document.customer.code,
                            customerFiscalCode=document.customer.fiscal_code,
                            customerVatCode=document.customer.vat_code,
                            customerHomepage="N/D",
                            notes="- CLIENTE NON CENSITO!",
                        ),
                        coordinates=get_coordinates(
                            address_string, google_api_key, caching=False
                        ),
                        hidden=False,
                        style="Customers",
                    )
                )
                unknown_customer_documents += 1

            logger.info(
                f"Added {len(documents)} unknown addresses for unknown customer {documents[0].customer.code} ({documents[0].customer.name})"
            )

        logger.warning(
            f"Added a total of {unknown_customer_documents} unknown customers"
        )

    return kmlb.kml(
        name="Estrazione clienti e fornitori",
        description=f"This KML was automatically generated by VeryEasyfatt at {datetime.datetime.now():%d-%m-%Y %H:%M:%S}.",
        collapsed=False,
        features=[
            kmlb.folder(
                "Clienti",
                description="Elenco completo delle anagrafiche clienti",
                loose_items=[
                    location.to_kml() for location in sorted(customer_locations)
                ],
                collapsed=True,
            ),
            kmlb.folder(
                "Fornitori",
                description="Elenco completo delle anagrafiche fornitori",
                loose_items=[
                    location.to_kml() for location in sorted(supplier_locations)
                ],
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
                "https://maps.google.com/mapfiles/kml/paddle/red-circle.png",  # Icon
                ("#ff0000", 100),  # Icon color
                1.0,  # Icon scale
                ("#ffffff", 100),  # Label color
                1.0,  # Label size
            ),
            kmlb.point_style(
                "Suppliers",  # Point style name
                "https://maps.google.com/mapfiles/kml/paddle/red-circle.png",  # Icon
                ("#ffff00", 100),  # Icon color
                1.0,  # Icon scale
                ("#ffffff", 100),  # Label color
                1.0,  # Label size
            ),
        ],
    )


def populate_cache(
    google_api_key,
    addresses=None,
    database_path: Union[str, Path, None] = None,
    dry_run=False,
):
    if addresses is None and database_path is None:
        raise Exception("Addresses and database path cannot be both None")

    if database_path is not None:
        addresses = get_all_addresses(database_path)
    else:
        if not isinstance(addresses, list):
            raise Exception("Addresses must be a list of CustomerAddress objects")

        if not all([isinstance(address, CustomerAddress) for address in addresses]):
            raise Exception("Addresses must be a list of CustomerAddress objects")

    # Use a rate limiter to avoid Google API rate limits
    bulk_geocoder = RateLimiter(
        geopy.geocoders.GoogleV3(api_key=google_api_key).geocode,
        min_delay_seconds=1 / 5,  # Max 5 requests per second
        swallow_exceptions=False,
    )

    logger.info("Cache initialization started (this may take a while...)")
    for address in addresses:
        if dry_run:
            logger.debug(
                f"Search for '{address.address} {address.postcode}, {address.city}, {address.country}'"
            )
            continue

        search_result = search_location(
            address=f"{address.address} {address.postcode}, {address.city}, {address.country}",
            geocoder=bulk_geocoder,  # Use the rate limited geocoder
        )
        logger.debug(f"Search returned {search_result}")

    unique_customers = set(
        [address.code for address in addresses if address.is_customer]
    )
    unique_suppliers = set(
        [address.code for address in addresses if not address.is_customer]
    )

    logger.info(
        f"Cache initialization completed successfully ({len(addresses)} addresses processed for {len(unique_customers) + len(unique_suppliers)} customers/suppliers)"
    )
    logger.info(
        f"Total processed customers: {len(unique_customers)} ({len([ addr for addr in addresses if addr.is_customer])} addresses)"
    )
    logger.info(
        f"Total processed suppliers: {len(unique_suppliers)} ({len([ addr for addr in addresses if not addr.is_customer])} addresses)"
    )


def get_all_addresses(database_path: Union[str, Path]) -> list[CustomerAddress]:
    """Get all the addresses from the database.

    Args:
        database_path (Union[str, Path]): Path to the database file.

    Returns:
        list[CustomerAddress]: List of all the addresses.
    """
    database = EasyfattFDB(database_path, download_firebird=True)

    logger.info("Connecting to database...")
    with database.connect() as connection:
        logger.info("Connected to database")

        anagrafiche = [
            CustomerAddress(**item, is_primary=True)
            for item in connection.cursor()
            .execute(
                """
                    SELECT anag."CodAnagr", ANAG."Nome", ANAG."Indirizzo", ANAG."Cap", ANAG."Citta", ANAG."Prov", IIF(naz."NomeNazionePrint" IS NULL, 'Italia', naz."NomeNazionePrint") AS "Nazione", IIF(anag."Cliente" = 1, 1, 0) AS "IsCustomer", IIF(anag."Fornitore" = 1, 1, 0) AS "IsSupplier", anag."CodiceFiscale", anag."PartitaIva", anag."HomePage"
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
                    SELECT anag."CodAnagr", td."Nome", td."Indirizzo", td."Cap", td."Citta", td."Prov", IIF(naz."NomeNazionePrint" IS NULL, 'Italia', naz."NomeNazionePrint") AS "Nazione", IIF(anag."Cliente" = 1, 1, 0) AS "IsCustomer", IIF(anag."Fornitore" = 1, 1, 0) AS "IsSupplier", td."CodDest", anag."CodiceFiscale", anag."PartitaIva", anag."HomePage"
                    FROM "TAnagrafica" AS anag
                    RIGHT JOIN "TAnagraficaDest" td ON td."IDAnagr" = ANAG."IDAnagr"
                    LEFT JOIN "TNazioni" naz ON td."Nazione" = naz."NomeNazione";
                """
            )
            .fetchallmap()
        ]

    # Elenco ordinato di tutte le anagrafiche (con indirizzi primari e secondari)
    return sorted(
        anagrafiche + anagrafiche_indirizzi_extra,
        key=lambda x: (x.code, not x.is_primary, x.alias),
    )
