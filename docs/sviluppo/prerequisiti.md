---
layout: default
title: Prerequisiti
parent: Sviluppo
nav_order: 1
---

# Prerequisiti
Per partecipare allo sviluppo dell'**applicativo** vero e proprio saranno necessari i seguenti prerequisiti:
- `python` (>3.9)
- `uv`

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

### Installazione `uv`

1. Installa [**`uv`**](https://docs.astral.sh/uv/getting-started/installation/):
   ```
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
1. **Riavvia la shell**

### Installazione dipendenze Python
Una volta installati i software necessari, bisognerà installare anche le **dipendenze** che permetteranno al programma di funzionare.

Questo si può fare con il comando:
```
uv sync
```

> Ora è possibile eseguire i singoli file Python usando il comando:
> ```
> uv run python [file_da_eseguire]
> ```
{: .highlight}

## Pacchetti per la documentazione
> Sotto questa categoria ricadono tutti i pacchetti non necessari all'esecuzione del programma o alla sua compilazione, ma che invece vengono utilizzati per testare localmente la documentazione che stai leggendo in questo momento 😃
{: .note}
Una volta effettuati tutti i passi spiegati di seguito sarà possibile vedere la documentazione nel proprio browser tramite il comando `uv run poe docs`

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
uv run build
```

#### Release
```
uv run release
```
