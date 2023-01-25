---
layout: default
title: Integrazione con RouteXL
parent: Guida utente
---
# Integrazione con RouteXL
{: .no_toc}
<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

## Cos'è RouteXL?
[**RouteXL**](https://www.routexl.it/) è un pianificatore di itinerari stradali verso destinazioni multiple.

Tramite un algoritmo intelligente permette di ordinare gli indirizzi in modo da **minimizzare la durata** totale del percorso.

## Come avviene l'integrazione?
Il programma rilascia un file CSV, il cui contenuto andrà poi incollato nella finestra di importazione di RouteXL.

<img src="{{ site.baseurl }}/assets/images/routexl-import.png">

## Gestione degli orari di consegna
Il programma permette la gestione degli orari di consegna per ogni singolo cliente.
> _Ad esempio:_
> _Mario Rossi accetta consegne dalle 10:00 alle 15:00, mentre Bianchi S.P.A. accetta consegne dalle 09:00 alle 18:00_
{: .highlight}

Questo però è possibile solo se nella cartella in cui si trova l'eseguibile è **presente** anche il **file** *`ExportClienti.xlsx`* ([**qui**](#come-generare-il-file-exportclientixlsx) la guida su come generarlo) e:
1. TUTTI i clienti hanno un **Codice cliente**
1. E' definita la colonna **`Extra 1`** (_ossia il campo "Libero 1"_)

### Come generare il file `ExportClienti.xlsx`?

> Affinchè il file generato risulti **valido** bisognerà **obbligatoriamente** seguire i seguenti passi:
> 1. Definire e **valorizzare** correttamente il campo "Intervallo consegne" per ogni > cliente
> 1. Controllare che ogni cliente abbia un proprio "**Codice cliente**" univoco.
> 1. **Esportare** tutti i clienti in **XLSX**
{: .warning}

#### Definire il campo "Intervallo consegne"
1. Andare nella scheda **"Cliente"**.
2. Per ogni Cliente definire un **valore valido** all'interno del campo personalizzato "_**Varie > Libero 1**_"

> E' possibile **rinominare** il campo "_Libero 1_" per una **miglior leggibilità** (ad esempio "Orario consegne" o "Intervalli di consegna").
> 
> Il nome infatti non è importante, in quanto in fase di export verrà **sempre** salvato come "**Extra N**" (dove N è il numero del campo).
>
> Per rinominarlo andare su "_Opzioni > Clienti e Fornitori > Nomi campi aggiuntivi_".
{: .note}

<img src="{{ site.baseurl }}/assets/images/easyfatt-clienti-lista.png" />

#### Controllare il "Codice cliente" di ogni cliente
1. Andare nella scheda **"Cliente"**.
1. Per ogni Cliente controllare che il campo "_Anagrafica > Codice_" sia **valorizzato correttamente** (_non deve essere vuoto_)

#### Esportare i clienti
1. Andare nella scheda **"Cliente"**.
1. Selezionare **tutti i clienti** (_consiglio: selezionare il primo e poi spuntare l'ultimo mantenendo premuto il tasto Shift_)
1. Cliccare su "_**Utilità** > **Esporta** con Excel/OpenOffice/LibreOffice_"
1. Selezionare "**Microsoft Excel**" e cliccare su OK
1. Salvare il file **nella stessa cartella** del programma


<img src="{{ site.baseurl }}/assets/images/easyfatt-clienti-export.png" />
