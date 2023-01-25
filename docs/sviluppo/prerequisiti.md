---
layout: default
title: Prerequisiti
parent: Sviluppo
nav_order: 1
---

# Prerequisiti
Per partecipare allo sviluppo dell'**applicativo** vero e proprio saranno necessari i seguenti prerequisiti:
- `python` (>3.9)
- `poetry`
- `pipx` (_consigliato_)

Per testare visivamente le modifiche alla **documentazione** invece, sarà necessario avere installato:
- `ruby`
- `gem`
- `jekyll`

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
- TOC
{:toc}
</details>


## Pacchetti per lo sviluppo
> Questi pacchetti sono **fondamentali** per lo sviluppo e compilazione del programma finale.
{: .warning}

### Installazione `pipx` e `poetry`
> L'installazione di `poetry` può essere effettuata anche senza utilizzare `pipx`, ma l'ho preferito per una questione di semplicità rispetto agli altri metodi.
{: .note}

1. Installa [**`pipx`**](https://github.com/pypa/pipx#install-pipx):
	```
	python -m pip install --user pipx
	```	
1. Aggiungi `pipx` alla variabile d'ambiente `PATH`:
	```
	pipx ensurepath
	```	
1. Installa [**`poetry`**](https://python-poetry.org/docs/#installing-with-pipx):
   ```
   pipx install poetry
   ```
1. **Riavvia la shell**

### Installazione dipendenze Python
Una volta installati i software necessari, bisognerà installare anche le **dipendenze** che permetteranno al programma di funzionare.

Questo si può fare con il comando:
```
poetry install
```

> Ora è possibile eseguire i singoli file Python usando il comando:
> ```
> poetry run python [file_da_eseguire]
> ```
{: .highlight}

## Pacchetti per la documentazione
> Sotto questa categoria ricadono tutti i pacchetti non necessari all'esecuzione del programma o alla sua compilazione, ma che invece vengono utilizzati per testare localmente la documentazione che stai leggendo in questo momento 😃
{: .note}
Una volta effettuati tutti i passi spiegati di seguito sarà possibile vedere la documentazione nel proprio browser tramite il comando `poetry run poe docs`

### Installazione `ruby`
Segui le istruzioni contenute nel [sito web ufficiale](https://jekyllrb.com/docs/installation/windows/#installation-via-rubyinstaller) di Jekyll.

### Installazione `gem`
Segui le istruzioni contenute nel [sito web ufficiale](https://rubygems.org/pages/download) di RubyGem.

### Installazione `jekyll`
```
gem install jekyll bundler
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
