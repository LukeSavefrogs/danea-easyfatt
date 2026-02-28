# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Impostando la configurazione `features.kml_generation.location_search_type` a `manual`, ora è possibile scegliere manualmente l'indirizzo da restituire per ogni segnaposto del KML tra quelli trovati tramite l'API di Geocoding di Google nel caso in cui questa restituisca più risultati per un unico indirizzo. Vedi issue [#172](https://github.com/LukeSavefrogs/danea-easyfatt/issues/172).

**Formatter**:

- Aggiunti parametri `separator` e `prefix`
- Aggiunte `Exception` personalizzate per il progetto

### Fixed

- Ora l'**encoding** di default dell'interprete Python è impostato a **`UTF-8`** invece di essere platform-dependent. Il programma non crasherà più in caso di caratteri speciali (come `→`), nemmeno durante i test automatici. Risolve issue [#141](https://github.com/LukeSavefrogs/danea-easyfatt/issues/141).

### Changed

- Ora durante la fase di Geocoding degli indirizzi tramite l'API Google Geocoding, se vengono riscontrati errori, questi vengono mostrati tutti insieme solo al termine dell'intera operazione.
- Rimosso il controllo dei file obbligatori prima che venga mostrato il menu di scelta operazione. Risolve issue [#140](https://github.com/LukeSavefrogs/danea-easyfatt/issues/140).

**Formatter**:

- Rinominato parametro `allow_attribute_access` in `sandboxed`
- Spostato modulo `shared.formatter` in un pacchetto separato

## [v1.4.7] - 2023-10-16

### Added

- Ora è possibile eseguire la ricerca dei segnaposti Google in 2 modalità: `strict` e `postalcode`. Questa opzione è personalizzabile solo tramite il file di configurazione alla voce [`features.kml_generation.location_search_type`](https://lukesavefrogs.github.io/danea-easyfatt/utente/configurazione.html#featureskml_generationlocation_search_type). Vedi issue [#126](https://github.com/LukeSavefrogs/danea-easyfatt/issues/126).

## [v1.4.6] - 2023-10-12

### Changed

- Rinominato parametro `geocoder` in `geocoder_fn` per la funzione `search_location` per esprimere meglio la tipologia di parametro richiesta.
- Corretto bug che causava la visualizzazione dei messaggi di logging a livello `DEBUG` anche se nel file di configurazione era impostato ad un altro livello. Questo bug avveniva solo durante la generazione del KML. Risolve issue [#129](https://github.com/LukeSavefrogs/danea-easyfatt/issues/129).

## [v1.4.5] - 2023-10-12

### Changed

- Ora la funzione `generate_kml` restituisce una stringa KML invece di creare il file.
- Ora la funzione `search_location` restituisce errore nel caso la chiamata al Geocoder di Google trovasse più risultati per un unico indirizzo (vedi issue [#126](https://github.com/LukeSavefrogs/danea-easyfatt/issues/126)).

## [v1.4.4] - 2023-09-20

### Fixed

- Ora nel caso di un'anagrafica sia cliente che fornitore, il segnaposto viene creato in entrambe le cartelle invece di solo la cartella "Fornitori". Risolve issue [#112](https://github.com/LukeSavefrogs/danea-easyfatt/issues/112).

## [v1.4.3] - 2023-09-13

### Fixed

- Corretto bug introdotto nella `v1.4.2` (_commit [`c0df440`](https://github.com/LukeSavefrogs/danea-easyfatt/commit/c0df4407014dd866342d0fe0a432bbdd089eb159)_) per cui il livello di logging dei messaggi mostrati a video era sempre impostato a `DEBUG`.

## [v1.4.2] - 2023-09-13

### Fixed

- Corretto bug per cui il file di log veniva sempre scritto con il livello della configurazione utente invece di `DEBUG`.
- Aggiornata versione di `easyfatt-db-connector` per correggere l'issue [#106](https://github.com/LukeSavefrogs/danea-easyfatt/issues/106) senza dover disattivare il cast ai tipi corretti (_commit [`27d14b8`](https://github.com/LukeSavefrogs/danea-easyfatt/commit/27d14b8c3b32cb53da3ee478060f697acab3f05b)_).

## [v1.4.1] - 2023-09-12

### Added

- Aggiunti i seguenti valori alla **formattazione personalizzata** del segnaposto nel KML: `customerFiscalCode` (_codice fiscale_), `customerVatCode` (_partita IVA_), `customerHomepage` (_homepage_). Per maggiori informazioni vedi issue [#98](https://github.com/LukeSavefrogs/danea-easyfatt/issues/98).

### Fixed

- Corretto bug introdotto con la versione `v1.4.0` che causava il mancato caricamento della configurazione utente presente nella cartella di esecuzione del programma. Risolve issue [#105](https://github.com/LukeSavefrogs/danea-easyfatt/issues/105).
- Corretto bug che causava il crash del programma nel raro caso in cui fossero presenti caratteri non compatibili con l'encoding `cp1252`. Ora il file `.DefXml` viene aperto e letto con l'encoding `UTF8`. Risolve issue [#107](https://github.com/LukeSavefrogs/danea-easyfatt/issues/107).
- Corretto bug che causava il crash del programma nel caso ci fossero prodotti all'interno del file `.DefXml` con quantità decimale. Risolve issue [#106](https://github.com/LukeSavefrogs/danea-easyfatt/issues/106).

## [v1.4.0] - 2023-09-11

### Added

- Aggiunto file di log a livello `DEBUG` nel percorso `./logs/YYYMMDD_hhmmss.log`. Risolve issue [#87](https://github.com/LukeSavefrogs/danea-easyfatt/issues/87).

**Tests**:

- Aggiunti test funzionali e di no-regression per il modulo `veryeasyfatt.app.process_csv`.

### Changed

- Aggiunto logging handler `logging.NullHandler()` ai logger dei moduli applicativi. In questo modo finchè viene inizializzato il root logger, i messaggi verranno mostrati a schermo, mentre durante i test automatici (in assenza di root logger) non verrà mostrato alcun log in output.
- Adesso la configurazione è disponibile globalmente per tutti i moduli del progetto attraverso l'oggetto `settings` del modulo `veryeasyfatt.configuration`. Risolve issue [#96](https://github.com/LukeSavefrogs/danea-easyfatt/issues/96).

### Fixed

- Corretto bug che causava il crash del programma in modalità "generazione CSV" se il file `.DefXml` passato conteneva un solo documento. Risolve issue [#89](https://github.com/LukeSavefrogs/danea-easyfatt/issues/89).
- Corretto bug introdotto con la configurazione globale, che causava un mescolamento errato della configurazione se questa veniva ricaricata da un'altro file. La strategia di "merge" di `Dynaconf` nel caso di liste contenenti solo tipi primitivi (`str`, `int`, `bool`, ecc..) infatti prevedeva il merge, mentre era necessario che in tal caso sostituisse i valori. Per maggiori informazioni vedi issue [dynaconf/dynaconf#999](https://github.com/dynaconf/dynaconf/issues/999).

## [v1.3.2] - 2023-09-05

### Added

- Ora i segnaposti del KML vengono ordinati per nome prima di essere esportati su file. Risolve issue [#95](https://github.com/LukeSavefrogs/danea-easyfatt/issues/95).
- Aggiunta possibilità di copiare il contenuto del file CSV negli appunti. Risolve issue [#94](https://github.com/LukeSavefrogs/danea-easyfatt/issues/94).
- Aggiunta possibilità di personalizzare il valore contenuto nel tag KML `<Placemark><description></description></Placemark>`

### Changed

- Ora il peso complessivo della spedizione viene direttamente stampato a schermo. In precedenza essendo stampato come log a livello `INFO` poteva sparire se il livello minimo veniva alzato (ad esempio a `WARNING`).

### Fixed

- Corretto `FutureWarning` mostrato in seguito all'aggiornamento di `pandas` alla versione `2.1.0`.
- Corretto bug che causava un'eccezione se **nessun documento** (tag `Document`) di carico nel file `.DefXml` aveva il tag `TransportedWeight` valorizzato. Risolve issue [#90](https://github.com/LukeSavefrogs/danea-easyfatt/issues/90).
- Corretto bug che causava la duplicazione di segnaposti nel caso in cui ci fossero documenti con indirizzi di consegna sconosciuti (non salvati su DB). Risolve issue [#86](https://github.com/LukeSavefrogs/danea-easyfatt/issues/86).
- Ora gli indirizzi nel documento e sul database vengono tutti trasformati in minuscolo prima di essere confrontati per evitare falsi positivi (es. `Via XX Settembre` e `VIA XX SETTEMBRE` interpretati come due indirizzi diversi).

## [v1.3.1] - 2023-09-01

### Added

- Aggiunto supporto per formattazione user-friendly (ad esempio `{var:s->uppercase}`).

### Changed

- Aggiunto supporto per formattazione user-friendly alle voci di configurazione `features.kml_generation.placemark_title` e `options.output.csv_template`. Risolve issue [#17](https://github.com/LukeSavefrogs/danea-easyfatt/issues/17).

## [v1.3.0] - 2023-08-31

### Added

- Aggiunta personalizzazione del titolo del segnaposto. Funzionalità richiesta nell'issue [#17](https://github.com/LukeSavefrogs/danea-easyfatt/issues/17).
- Aggiunta la possibilità di bypassare la cache alla funzione `caching.persist_to_file` quando viene passato un certo parametro alla funzione decorata (configurabile tramite il parametro `enabled`).

### Changed

- Cambiata struttura del progetto da `./src/` a `./src/package/`
- Aggiunto limite di chiamate al secondo alle API di Google Maps e retry automatico dei primi 3 fallimenti.
- Ora è possibile passare un oggetto `Geocoder` alla funzione `search_location()` invece di quello di default.
- Riportato livello di logging di default a `INFO` (era stato portato `DEBUG` con la commit [08a64de](https://github.com/LukeSavefrogs/danea-easyfatt/commit/08a64dec5de388e79fe8e3044e8eb3eb872c0e0e) del 7 febbraio).

### Fixed

- Fixato bug che avrebbe impedito l'**aggiunta di alcuni indirizzi**, se e solo se questi non fossero legati a clienti conosciuti e si trovassero ultimi (quindi senza nessun documento appartenente ad un cliente conosciuto dopo) nel documento `.DefXml`.
- Ora il `RateLimiter` delle API Google non ignora più le eccezioni, ma le rilancia.
- Ora la cache delle chiamate API al servizio Geocoding di Google in caso di clienti sconosciuti viene correttamente ignorata.
- Ora il livello di logging scelto da configurazione si riflette sul Root logger, nascondendo o mostrando quindi tutti i messaggi, anche dei moduli figlio.

## [v1.2.2] - 2023-08-30

### Added

- Aggiunta geocodifica tramite API di Google Maps per gli indirizzi esportati nel KML in modo da rendere istantanea l'apertura di questi file tramite Google Earth. Implementa issue [#17](https://github.com/LukeSavefrogs/danea-easyfatt/issues/17).
- Aggiunta voce di configurazione `features.kml_generation.google_api_key` contenente la chiave per l'accesso alle API di Google Maps utilizzate per fare Geocoding degli indirizzi esportati nel KML.
- Aggiunta nuova funzionalità per l'inizializzazione della cache delle API di Google Maps, completa di versione "dry-run" (simula le chiamate e stampa solo il report finale) e controparti CLI.

### Changed

- Cambiato formato del titolo dei segnaposti esportati in KML da `{name} ({code}) {notes}` a `{name:.10} {code}` come richiesto nell'issue [#17](https://github.com/LukeSavefrogs/danea-easyfatt/issues/17).
- Aggiunta possibilità al decoratore `@caching.persist_to_file()` di scegliere i parametri da aggiungere alla cache.

**Tests**:

- Disabilitato controllo di versione durante l'esecuzione dei test automatici.
- Modificata modalità con cui veniva controllata la configurazione nei test.
- Rimosso parametro `--failfast` dal comando eseguito per lanciare i test (automatici e non). Questo impediva di vedere il risultato completo dei test fermandosi solo al primo test fallito.

### Fixed

- Corretto bug per cui in caso di errori HTTP durante il controllo di nuovi aggiornamenti il programma crashava con un messaggio non inerente al problema.

**Tests**:

- Corretto errore di battitura nei test che causava il loro fallimento ad ogni run.
