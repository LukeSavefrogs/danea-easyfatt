""" Entry point of the wrapper. """
import datetime
import sys
import webbrowser
import argparse
from veryeasyfatt.app.constants import ApplicationGoals

import veryeasyfatt.bundle as bundle
import veryeasyfatt.updater as updater

from packaging.version import Version
from rich.logging import RichHandler
import logging

default_handler = logging.StreamHandler(sys.stdout)
default_handler.setFormatter(
    logging.Formatter(
        fmt="[%(asctime)s] %(levelname)-8s %(message)s", datefmt="%d-%m-%Y %H:%M:%S"
    )
)

logger = logging.getLogger("danea-easyfatt")
logger.addHandler(default_handler)
logger.setLevel(logging.DEBUG)

LOG_FILENAME = (
    bundle.get_execution_directory()
    / f"logs/{datetime.datetime.today():%Y%m%d_%H%M%S}.log"
)
LOG_FILENAME.parent.mkdir(parents=True, exist_ok=True)
FILE_HANDLER = logging.FileHandler(LOG_FILENAME, mode="w+", encoding="utf-8")
FILE_HANDLER.setFormatter(
    logging.Formatter(
        fmt="[%(asctime)s] %(levelname)-8s %(message)s", datefmt="%d-%m-%Y %H:%M:%S"
    )
)
FILE_HANDLER.setLevel(logging.DEBUG)
logger.addHandler(FILE_HANDLER)

# The Rich handler will be used if `--disable-rich-handler` is not passed
rich_handler = RichHandler(
    rich_tracebacks=True,
    omit_repeated_times=False,
    log_time_format="[%d-%m-%Y %H:%M:%S]",
)


# Windows specific definitions
if sys.platform != "win32":
    logger.critical("This program is available only for the Windows platform.")
    sys.exit(1)

import veryeasyfatt.app.main as application
from veryeasyfatt.configuration import settings


# -----------------------------------------------------------
#                        Inizio codice
# -----------------------------------------------------------
def main():
    # ==================================================================
    #                     Parametri linea di comando
    # ==================================================================
    parser = argparse.ArgumentParser(
        prog=bundle.get_executed_file().name,
        description="Easyfatt made even easier!",
        epilog="Author: Luca Salvarani (email: lucasalvarani99@gmail.com - github: @LukeSavefrogs)",
        add_help=True,
    )
    parser.add_argument(
        "-c",
        "--config",
        required=False,
        help="Specify a custom TOML configuration file.",
        dest="configuration_file",
        metavar="FILENAME",
        type=str,
        default=None,
    )
    parser.add_argument(
        "-V",
        "--version",
        help="Show the current version and exit.",
        action="version",
        version=f"v{updater.get_current_version()}",
    )
    parser.add_argument(
        "--disable-version-check",
        help="Disable the version check process.",
        dest="enable_version_check",
        action="store_false",
        default=True,
    )
    parser.add_argument(
        "--disable-rich-logging",
        help="Disable the Rich logging handler (used for testing).",
        dest="enable_rich_logging",
        action="store_false",
        default=True,
    )
    parser.add_argument(
        "--goal",
        help="Specify the goal of the program (used for testing).",
        dest="goal",
        type=str,
        default=None,
        choices=ApplicationGoals.values(),
    )
    cli_args = parser.parse_args()

    if cli_args.configuration_file is not None:
        print("Loading custom configuration file: ", cli_args.configuration_file)
        settings.reload_settings(cli_args.configuration_file)

    # Configure loggers
    if cli_args.enable_rich_logging:
        stream_handlers = [
            handler
            for handler in logger.handlers
            if type(handler) in [logging.StreamHandler, RichHandler]
        ]
        for handler in stream_handlers:
            logger.removeHandler(handler)
        logger.addHandler(rich_handler)

    try:
        stream_handlers = [
            handler
            for handler in logger.handlers
            if type(handler) in [logging.StreamHandler, RichHandler]
        ]
        for handler in stream_handlers:
            handler.setLevel(logging.getLevelName(settings.log_level))
    except ValueError:
        logger.warning(
            f"Invalid log level '{settings.log_level}'. Use one of the following: "
            + ", ".join(logging._nameToLevel.keys())
        )
        return False

    logger.debug(f"Configurazione in uso: \n{settings.to_dict()}")
    logger.debug(f"CLI parameters: {cli_args}")

    logger.debug(f"Execution directory: '{bundle.get_execution_directory()}'")
    logger.debug(f"Bundle directory   : '{bundle.get_bundle_directory()}'")
    logger.debug(f"Root directory     : '{bundle.get_root_directory()}'")

    # ==================================================================
    #                       Controllo di versione
    # ==================================================================
    if not cli_args.enable_version_check:
        logger.warning(
            "Il controllo versione è stato disattivato tramite CLI (--disable-version-check)."
        )
    else:
        try:
            if updater.update_available():
                latest_release = updater.get_latest_version()
                latest_version = Version(updater.get_latest_version())
                current_version = Version(updater.get_current_version())

                logger.warning(
                    f"An update is available (remote is '{latest_version}', while current is '{current_version}')"
                )
                webbrowser.open(
                    updater.get_latest_release()["url"], new=0, autoraise=True
                )

                return False
            else:
                logger.debug(f"La tua versione è aggiornata! :)")
        except Exception:
            logger.exception("Errore in fase di controllo aggiornamenti")

            logger.fatal(
                "Impossibile continuare. Assicurati di fare uno screenshot di questa schermata e condividerla con lo sviluppatore."
            )

            return False

    try:
        application.main(cli_args.goal)
    except Exception:
        logger.exception("Eccezione inaspettata nell'applicazione")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception("Eccezione inaspettata nella funzione main")
    finally:
        input("Premi [INVIO] per terminare il programma...")
