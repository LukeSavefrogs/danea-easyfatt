[![Stato ultimo rilascio](https://github.com/LukeSavefrogs/danea-easyfatt/actions/workflows/release.yml/badge.svg)](https://github.com/LukeSavefrogs/danea-easyfatt/actions/workflows/release.yml) 
[![Documentazione](https://github.com/LukeSavefrogs/danea-easyfatt/actions/workflows/documentation.yml/badge.svg)](https://github.com/LukeSavefrogs/danea-easyfatt/actions/workflows/documentation.yml)

## Utilizzo
### Esportare 
![picture 1](images/fc0b02a29028a491d001791e65fc306777051aed35e7229736e8fec70b35ca8e.png)  


## Sviluppo
### TODO
- [ ] Aggiungere GUI
- [ ] Aggiungere file di configurazione
- [ ] Aggiungere visualizzazione di: peso totale dell'ordine, guadagno e importo
- [ ] Aggiungere visuale di insieme degli ordini tramite [Google Earth](https://developers.google.com/kml/documentation?hl=en)


### Installazione dei software necessari
1. Installa [**`pipx`**](https://github.com/pypa/pipx#install-pipx):
	```
	python -m pip install --user pipx
	pipx ensurepath
	```	
2. Installa [**`poetry`**](https://python-poetry.org/docs/#installing-with-pipx):
   ```
   pipx install poetry
   ```
3. **Riavvia la shell**


### Utilizzo
1. Installa i pacchetti necessari:
	```
	poetry install
	```
2. Lancia lo script:
	```
	poetry run python src/main.py
	```


### Scripts
#### Build
Lancia il processo di build:
```
poetry run build
```

#### Release
```
poetry run release
```

Creazione di un eseguibile con GUI:
- https://www.pythonguis.com/tutorials/packaging-pyqt5-pyside2-applications-windows-pyinstaller/
- https://build-system.fman.io/pyqt5-tutorial