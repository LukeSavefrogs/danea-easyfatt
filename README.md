[![Stato ultimo rilascio](https://github.com/LukeSavefrogs/danea-easyfatt/actions/workflows/release.yml/badge.svg)](https://github.com/LukeSavefrogs/danea-easyfatt/actions/workflows/release.yml)

## Sviluppo
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