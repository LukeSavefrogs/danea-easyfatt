""" Entry point of the application. """
from io import StringIO
import json
import os
from pathlib import Path
import subprocess
from typing import Optional
import logging

import pandas as pd
import pint

from rich.prompt import Confirm, IntPrompt

from veryeasyfatt.app.process_kml import generate_kml, populate_cache
from veryeasyfatt.app.process_xml import modifica_xml
from veryeasyfatt.app.process_csv import genera_csv

import veryeasyfatt.app.config_manager as configuration_manager
from veryeasyfatt.app.registry import find_install_location

import veryeasyfatt.bundle as bundle

logger = logging.getLogger("danea-easyfatt.application.core")

EASYFATT_DOCUMENT_DTYPE = {
    "CustomerCode": str,
    "CustomerPostcode": str,
    "CustomerVatCode": str,
    "CustomerTel": str,
}


# -----------------------------------------------------------
#                        Inizio codice
# -----------------------------------------------------------
def main(configuration_file: Optional[str] = None, goal: Optional[str] = None):
    # ==================================================================
    #                       Lettura configurazione
    # ==================================================================
    try:
        configuration = configuration_manager.get_configuration(configuration_file)
    except Exception as e:
        logger.critical(f"Errore in fase di recupero configurazione: {e}")
        return False

    if configuration["log_level"]:
        logging.getLogger("danea-easyfatt").setLevel(
            logging.getLevelName(configuration["log_level"])
        )

    logger.debug(f"Configurazione in uso: \n{json.dumps(configuration, indent=4)}")

    # ==================================================================
    #                     Controllo file richiesti
    # ==================================================================
    REQUIRED_FILES = [
        Path(configuration["files"]["input"]["easyfatt"]),
    ]
    missing_required_file = False
    for required_file in REQUIRED_FILES:
        if not required_file.resolve().exists():
            logger.critical(
                f"File richiesto '{required_file.resolve().absolute()}' non trovato."
            )
            missing_required_file = True

    if missing_required_file:
        return False

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

    if goal == "csv-generator":
        # 1. Modifico l'XML
        nuovo_xml: str
        if configuration["files"]["input"]["addition"] != "":
            try:
                # Aggiunge il contenuto di `additional_xml_file` all'interno di `easyfatt_xml`
                nuovo_xml = modifica_xml(
                    easyfatt_xml_file=Path(
                        configuration["files"]["input"]["easyfatt"]
                    ).resolve(),
                    additional_xml_file=Path(
                        configuration["files"]["input"]["addition"]
                    ).resolve(),
                )

                logger.info(f"Analisi e modifica XML terminata..")
            except Exception as e:
                logger.exception(f"Errore durante la modifica del file XML: {repr(e)}")
                return False
        else:
            nuovo_xml = (
                Path(configuration["files"]["input"]["easyfatt"]).resolve().read_text()
            )

        # 2. Genero il CSV sulla base del template
        try:
            righe_csv = genera_csv(
                xml_text=nuovo_xml,
                template_riga=configuration["options"]["output"]["csv_template"],
                customer_files=configuration["easyfatt"]["customers"][
                    "export_filename"
                ],
                extra_field_id=configuration["easyfatt"]["customers"]["custom_field"],
                default_shipping_interval=configuration["features"]["shipping"][
                    "default_interval"
                ],
            )

            # Salvo il csv su file
            with open(configuration["files"]["output"]["csv"], "w") as csv_file:
                csv_file.write("\n".join(righe_csv))

            logger.info(
                f"Creazione CSV '{configuration['files']['output']['csv']}' terminata.."
            )
        except Exception:
            logger.exception("Errore durante la generazione del file CSV.")
            return False

        # 3. Calcolo il peso totale della spedizione
        try:
            ureg = pint.UnitRegistry(
                autoconvert_offset_to_baseunit=True, on_redefinition="raise"
            )
            ureg.default_format = "~P"
            ureg.define("quintal = 100 * kg = q = centner")

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
                else ureg.Quantity(str(v).replace(".", "").replace(",", ".").lower())
                .to("g")
                .magnitude
            )

            df_weight_sum = df["TransportedWeight"].sum()
            peso_totale = (
                ureg.Quantity(df_weight_sum, "g")
                if not pd.isna(df_weight_sum)
                else ureg.Quantity(0, "g")
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
            f"Aprire il file '{configuration['files']['output']['csv']}'?",
            choices=["s", "n"],
        ):
            os.startfile(
                Path(configuration["files"]["output"]["csv"]).resolve(), "open"
            )
        print("\n")

    elif goal == "kml-generator":
        output_file = str(configuration["files"]["output"]["kml"]).strip()
        if output_file == "":
            output_file = bundle.get_execution_directory() / "output.kml"

        generate_kml(
            xml_filename=Path(configuration["files"]["input"]["easyfatt"]).resolve(),
            database_path=Path(configuration["easyfatt"]["database"]["filename"])
            .expanduser()
            .resolve(),
            output_filename=output_file,
            google_api_key=configuration["features"]["kml_generation"][
                "google_api_key"
            ],
            placemark_title=configuration["features"]["kml_generation"][
                "placemark_title"
            ],
        )
        logger.info(f"Creazione KMl '{output_file}' terminata..")

        try:
            google_earth_path = find_install_location(
                r"SOFTWARE\Google\Google Earth Pro"
            )
            logger.info(f"Google Earth path: {google_earth_path}")

            if Confirm.ask("Aprire il file KML su Google Earth?", choices=["s", "n"]):
                subprocess.Popen(
                    [
                        str(Path(google_earth_path, "googleearth.exe").resolve()),
                        str(output_file),
                    ],
                    shell=True,
                    cwd=str(google_earth_path),
                )
        except Exception as e:
            logger.error(f"Errore in fase di apertura Google Earth: {e}")

    elif goal.startswith("initialize-geo-cache"):
        populate_cache(
            google_api_key=configuration["features"]["kml_generation"][
                "google_api_key"
            ],
            database_path=Path(configuration["easyfatt"]["database"]["filename"])
            .expanduser()
            .resolve(),
            dry_run=goal.endswith("-dryrun"),
        )


# Per compilare: pyinstaller --onefile --clean .\src\main.py
if __name__ == "__main__":
    try:
        main(r"D:\Progetti\danea-automation\tests\data\veryeasyfatt.config.toml")
    except Exception as e:
        logger.exception("Eccezione inaspettata nella funzione main")
    finally:
        input("Premi [INVIO] per terminare il programma...")
        pass
