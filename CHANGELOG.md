# Changelog

## [Unreleased]

### Fixed

- Corretto `FutureWarning` mostrato in seguito all'aggiornamento di `pandas` alla versione `2.1.0`.
- Corretto bug che causava un'eccezione se **nessun documento** (tag `Document`) di carico nel file `.DefXml` aveva il tag `TransportedWeight` valorizzato. Risolve issue [#90](https://github.com/LukeSavefrogs/danea-easyfatt/issues/90).

## [v1.3.1] - 2023-09-01

### Added

- Aggiunto supporto per formattazione user-friendly (ad esempio `{var:s->uppercase}`).

### Changed

- Aggiunto supporto per formattazione user-friendly alle voci di configurazione `features.kml_generation.placemark_title` e `options.output.csv_template`. Risolve issue [#17](https://github.com/LukeSavefrogs/danea-easyfatt/issues/17).

## [v1.3.0] - 2021-08-31

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