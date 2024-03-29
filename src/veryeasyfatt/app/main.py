""" Entry point of the application. """
from io import StringIO
import json
import os
from pathlib import Path
import subprocess
from typing import Optional
import logging

import pandas as pd
import pyperclip

from rich.prompt import Confirm, IntPrompt
from veryeasyfatt.app.constants import ApplicationGoals

from veryeasyfatt.app.process_kml import generate_kml, populate_cache
from veryeasyfatt.app.process_xml import modifica_xml
from veryeasyfatt.app.process_csv import genera_csv
from veryeasyfatt.app.registry import find_install_location
from veryeasyfatt.shared.measuring import unit_registry

from veryeasyfatt.configuration import settings

logger = logging.getLogger("danea-easyfatt.application.core")

EASYFATT_DOCUMENT_DTYPE = {
    "CustomerCode": str,
    "CustomerPostcode": str,
    "CustomerVatCode": str,
    "CustomerTel": str,
}


def require_files(required_files: list[Path]) -> None:
    """Verifica che i file richiesti esistano.

    Args:
        required_files (list[Path]): Lista di file richiesti.

    Raises:
        Exception: Se uno dei file richiesti non esiste.
    """
    _separator = "\n → "

    missing_files = [
        file
        for file in map(Path, required_files)  # enforce Path type for all list elements
        if not file.resolve().exists()
    ]
    if missing_files:
        raise FileNotFoundError(
            f"The following required files were not found:{_separator}{_separator.join([str(file.resolve()) for file in missing_files])}"
        )


# -----------------------------------------------------------
#                        Inizio codice
# -----------------------------------------------------------
def main(goal: Optional[str] = None):
    if goal is None:
        print("Scegli l'operazione da effettuare:")
        print("1) Generatore CSV per RouteXL")
        print("2) Generatore KML per Google Earth")
        print("3) Inizializza cache geografica (Google Maps)")
        print("4) Simula inizializzazione cache geografica (Google Maps)")
        print("0) Esci")
        print()
        user_choice = IntPrompt.ask(
            "Quale azione desideri eseguire?",
            choices=["1", "2", "3", "4", "0"],
            default=0,
        )

        if user_choice == 0:
            return True
        elif user_choice == 1:
            goal = "csv-generator"
        elif user_choice == 2:
            goal = "kml-generator"
        elif user_choice == 3:
            goal = "initialize-geo-cache"
        elif user_choice == 4:
            goal = "initialize-geo-cache-dryrun"
        else:
            logger.error("Scelta non valida.")
            return False

    if goal == ApplicationGoals.CSV_GENERATOR.value:
        try:
            require_files([settings.files.input.easyfatt])
        except FileNotFoundError as e:
            logger.critical(e)
            return False

        # 1. Modifico l'XML
        nuovo_xml: str
        if settings.files.input.addition is not None:
            try:
                # Aggiunge il contenuto di `additional_xml_file` all'interno di `easyfatt_xml`
                nuovo_xml = modifica_xml()

                logger.info(f"Analisi e modifica XML terminata..")
            except Exception as e:
                logger.exception(f"Errore durante la modifica del file XML: {repr(e)}")
                return False
        else:
            nuovo_xml = (
                Path(settings["files"]["input"]["easyfatt"])
                .resolve()
                .read_text(encoding="utf8")
            )

        # 2. Genero il CSV sulla base del template
        try:
            righe_csv = genera_csv(xml_text=nuovo_xml)

            if Confirm.ask(
                f"Copiare negli appunti il contenuto del CSV?",
                choices=["s", "n"],
            ):
                pyperclip.copy("\n".join(righe_csv))
                logger.info("Righe CSV copiate negli appunti.")

            # Salvo il csv su file
            with open(settings["files"]["output"]["csv"], "w") as csv_file:
                csv_file.write("\n".join(righe_csv))

            logger.info(
                f"Creazione CSV '{settings['files']['output']['csv']}' terminata.."
            )
        except Exception:
            logger.exception("Errore durante la generazione del file CSV.")
            return False

        # 3. Calcolo il peso totale della spedizione
        try:
            df = pd.read_xml(
                StringIO(nuovo_xml),
                parser="etree",
                xpath="./Documents/Document",
                dtype=EASYFATT_DOCUMENT_DTYPE,  # type: ignore
            )

            # Effettuo una prima pulizia dei valori a solo scopo di visualizzazione.
            # Successivamente, per il calcolo del peso totale, converto tutti i valori a grammi.
            #
            # IMPORTANTE: Per evitare valori sballati nel totale sono costretto a
            #             trasformare il separatore decimale nel formato inglese (.)
            df["TransportedWeight"] = df["TransportedWeight"].map(
                lambda v: v
                if (v is None or pd.isnull(v))
                else unit_registry.Quantity(
                    str(v).replace(".", "").replace(",", ".").lower()
                )
                .to("g")
                .magnitude
            )

            df_weight_sum = df["TransportedWeight"].sum()
            peso_totale = (
                unit_registry.Quantity(df_weight_sum, "g")
                if not pd.isna(df_weight_sum)
                else unit_registry.Quantity(0, "g")
            )
            print(
                f"Peso totale calcolato: {peso_totale.to('kg')} ({peso_totale.to('q')} / {peso_totale.to('t')})"
            )

        except Exception as e:
            logger.exception("Errore in fase di calcolo peso totale")

        logger.info("Procedura terminata.")

        # ==================================================================
        #                     Apro file CSV generato
        # ==================================================================
        # Issue #20
        print("\n")
        if Confirm.ask(
            f"Aprire il file '{settings['files']['output']['csv']}'?",
            choices=["s", "n"],
        ):
            os.startfile(Path(settings["files"]["output"]["csv"]).resolve(), "open")
        print("\n")

    elif goal == ApplicationGoals.KML_GENERATOR.value:
        if settings.easyfatt.database.filename is None:
            logger.error(
                "Il file di database non è stato specificato nel file di configurazione."
            )
            return False

        if settings.features.kml_generation.google_api_key in [None, ""]:
            logger.error(
                "La chiave API di Google Geocoding non è stata specificata nel file di configurazione. "
                + "Seguire la guida al seguente URL: 'https://github.com/LukeSavefrogs/danea-easyfatt/issues/17#issuecomment-1699004094'"
            )
            return False

        try:
            require_files([settings.files.input.easyfatt])
        except Exception as e:
            logger.critical(e)
            return False

        logger.info("Inizio generazione contenuto KML...")

        kml_string = generate_kml()
        with open(settings.files.output.kml, "w") as file:
            file.write(kml_string)

        logger.info(f"Creazione KMl '{settings.files.output.kml}' terminata..")

        try:
            google_earth_path = find_install_location(
                r"SOFTWARE\Google\Google Earth Pro"
            )
            logger.info(f"Google Earth path: {google_earth_path}")

            if Confirm.ask("Aprire il file KML su Google Earth?", choices=["s", "n"]):
                subprocess.Popen(
                    [
                        str(Path(google_earth_path, "googleearth.exe").resolve()),
                        str(settings.files.output.kml),
                    ],
                    shell=True,
                    cwd=str(google_earth_path),
                )
        except Exception as e:
            logger.error(f"Errore in fase di apertura Google Earth: {e}")

    elif goal in [
        ApplicationGoals.INITIALIZE_GEO_CACHE.value,
        ApplicationGoals.INITIALIZE_GEO_CACHE_DRYRUN.value,
    ]:
        if settings.easyfatt.database.filename is None:
            logger.error(
                "Il file di database non è stato specificato nel file di configurazione."
            )
            return False

        if settings.features.kml_generation.google_api_key in [None, ""]:
            logger.error(
                "La chiave API di Google Geocoding non è stata specificata nel file di configurazione. "
                + "Seguire la guida al seguente URL: 'https://github.com/LukeSavefrogs/danea-easyfatt/issues/17#issuecomment-1699004094'"
            )
            return False

        populate_cache(
            google_api_key=settings.features.kml_generation.google_api_key,
            database_path=(
                Path(settings["easyfatt"]["database"]["filename"])
                .expanduser()
                .resolve()
            ),
            dry_run=goal == ApplicationGoals.INITIALIZE_GEO_CACHE_DRYRUN.value,
        )


if __name__ == "__main__":
    try:
        main(r"D:\Progetti\danea-automation\tests\data\veryeasyfatt.config.toml")
    except Exception as e:
        logger.exception("Eccezione inaspettata nella funzione main")
    finally:
        input("Premi [INVIO] per terminare il programma...")
        pass
