---
layout: default
title: Configurazione
parent: Guida utente
nav_order: 2
---
# Configurazione
A partire dalla versione [`v0.6.0`](https://github.com/LukeSavefrogs/danea-easyfatt/releases/tag/v0.6.0) è possibile modificare il comportamento del programma tramite il file di configurazione `veryeasyfatt.config.toml` all'interno della stessa cartella in cui è salvato il programma.

Un esempio di file di configurazione è il seguente, tratto dalla [configurazione di default](https://github.com/LukeSavefrogs/danea-easyfatt/blob/main/pyproject.toml){:target="_blank"} del programma:
```toml
# --------------------------------------------------------------
#                 Default configuration file
# --------------------------------------------------------------
log_level = "DEBUG"                        # Per la lista completa dei valori disponibili: https://docs.python.org/3/library/logging.html#logging-levels


[easyfatt.customers]
custom_field = 1                          # Numero del campo "Extra {N}"
export_filename = "./Soggetti.xlsx"       # Nome del file esportato dalla sezione clienti di EasyFatt

[files.input]
easyfatt = "./Documenti.DefXml"           # Percorso (relativo o assoluto) al file `*.DefXML` generato dal gestionale "Danea Easyfatt".
addition = "./PRIMARIGA.xml"              # Percorso (relativo o assoluto) al file `*.xml` con le righe da aggiungere come primo figlio del tag `Documents`.


[files.output]
csv = "./Documenti.csv"                   # Percorso (relativo o assoluto) al file CSV di output.


[options.output]
# Stringa utilizzata come template per OGNI riga del CSV. NON MODIFICARE I NOMI DEI PLACEHOLDER che iniziano per `eval_*`!
csv_template = "@{CustomerName} {CustomerCode}@{eval_IndirizzoSpedizione} {eval_CAPSpedizione} {eval_CittaSpedizione}(20){eval_intervalloSpedizione}^{eval_pesoSpedizione}^"
```

> Essendo ancora in **fase di sviluppo** il nome di queste impostazioni potrebbe **cambiare nel tempo**!
>
> _Questa pagina verrà costantemente aggiornata con le ultime informazioni utili.
> Assicurarsi di consultarla in caso di problemi._
{: .problem}

## `log_level`
Questa voce specifica il **livello di verbosità del logging**. Di default è impostata a `INFO`, ma può essere impostato a qualsiasi dei livelli definiti [nella documentazione](https://docs.python.org/3/library/logging.html#logging-levels).

> Valore di default
> 
> `DEBUG`
{: .note-title .fs-3 }

## `easyfatt.customers`
Questa sezione di configurazione regola il comportamento del programma verso l'**esportazione clienti** eseguita da **Easyfatt**.

### `easyfatt.customers.custom_field`

Indica il numero sequenziale del **campo personalizzato** `Libero {N}` (poi esportato come `Extra {N}`) utilizzato per definire l'**orario di consegna** per il singolo cliente.

> Valore di default
> 
> `1`
{: .note-title .fs-3 }

### `easyfatt.customers.export_filename`

Indica il percorso (assoluto o relativo) del file contenente l'estrazione da Easyfatt degli utenti.


> Valore di default
> 
> `./Soggetti.xlsx` o `./Soggetti.ods`
>
{: .note-title .fs-3 }

Se omesso verrà cercato il file `./Soggetti.xlsx` o `./Soggetti.ods` e verrà utilizzato il primo trovato (nell'ordine: `.xlsx` e poi `.ods`).


## `files.input`
Contiene impostazioni relative ai file utilizzati dal programma.

### `files.input.easyfatt`
Il file `.DefXml` ottenuto dall'**esportazione** dei **documenti "Ordine cliente"** da Easyfatt.

> Valore di default
> 
> `./Documenti.DefXml`
{: .note-title .fs-3 }


### `files.input.addition`
Il file `.xml` contenente il tag `Document` da aggiungere come **primo elemento** nel file `csv` generato. Questo servirà poi a [`RouteXL`]({{ site.baseurl }}/utente/routexl.html) come punto di partenza per calcolare le consegne.

> Valore di default
> 
> `./PRIMARIGA.xml`
{: .note-title .fs-3 }

Di seguito un **esempio** di un contenuto valido per il file:
```xml
<Document>
	<CustomerCode>00000</CustomerCode>
	<CustomerWebLogin></CustomerWebLogin>
	<CustomerName>{Nome Azienda}</CustomerName>
	<CustomerAddress>{Indirizzo}</CustomerAddress>
	<CustomerPostcode>{CAP}</CustomerPostcode>
	<CustomerCity>{Città}</CustomerCity>
	<CustomerProvince>{Provincia}</CustomerProvince>
	<CustomerCountry>{Italia}</CustomerCountry>
	<CustomerFiscalCode>{PartitaIVA}</CustomerFiscalCode>
	<CustomerTel>{Telefono}</CustomerTel>
	<CustomerCellPhone>{Cellulare}</CustomerCellPhone>
	<CustomerEmail>{Email}</CustomerEmail>
	<DeliveryName>{Nome per la consegna}</DeliveryName>
	<DeliveryAddress>{Indirizzo}</DeliveryAddress>
	<DeliveryPostcode>{CAP}</DeliveryPostcode>
	<DeliveryCity>{Città}</DeliveryCity>
	<DeliveryProvince>{Provincia}</DeliveryProvince>
	<DeliveryCountry>{Stato}</DeliveryCountry>
	<DocumentType>C</DocumentType>
	<Date>{Data}</Date>
	<Number>{Numero}</Number>
	<Numbering></Numbering>
	<CostDescription></CostDescription>
	<CostVatCode></CostVatCode>
	<CostAmount></CostAmount>
	<ContribDescription></ContribDescription>
	<ContribPerc></ContribPerc>
	<ContribSubjectToWithholdingTax></ContribSubjectToWithholdingTax>
	<ContribAmount></ContribAmount>
	<ContribVatCode></ContribVatCode>
	<TotalWithoutTax>+10</TotalWithoutTax>
	<VatAmount>+10</VatAmount>
	<WithholdingTaxAmount>0</WithholdingTaxAmount>
	<WithholdingTaxAmountB>0</WithholdingTaxAmountB>
	<WithholdingTaxNameB></WithholdingTaxNameB>
	<Total>+10</Total>
	<PriceList>Dom. OFFERTA</PriceList>
	<PricesIncludeVat>true</PricesIncludeVat>
	<TotalSubjectToWithholdingTax>0</TotalSubjectToWithholdingTax>
	<WithholdingTaxPerc>0</WithholdingTaxPerc>
	<WithholdingTaxPerc2>0</WithholdingTaxPerc2>
	<PaymentName>Contrassegno</PaymentName>
	<PaymentBank></PaymentBank>
	<PaymentAdvanceAmount></PaymentAdvanceAmount>
	<Carrier></Carrier>
	<TransportReason></TransportReason>
	<GoodsAppearance></GoodsAppearance>
	<NumOfPieces></NumOfPieces>
	<TransportDateTime></TransportDateTime>
	<ShipmentTerms></ShipmentTerms>
	<TransportedWeight></TransportedWeight>
	<TrackingNumber></TrackingNumber>
	<InternalComment></InternalComment>
	<CustomField1></CustomField1>
	<CustomField2></CustomField2>
	<CustomField3></CustomField3>
	<CustomField4></CustomField4>
	<FootNotes></FootNotes>
	<ExpectedConclusionDate></ExpectedConclusionDate>
	<SalesAgent></SalesAgent>
	<Rows>
		<Row>
			<Code></Code>
			<Description>QUESTA E' UNA RIGA DI TESTO PER EFFETTUARE TEST D'IMPORTAZIONE CORRETTA</Description>
			<Qty></Qty>
			<Um></Um>
			<Price></Price>
			<Discounts></Discounts>
			<VatCode Perc="22" Class="Imponibile" Description="Imponibile 22%">22</VatCode>
			<Total></Total>
			<Stock>false</Stock>
			<Notes></Notes>
		</Row>
	</Rows>
</Document>
```

## `files.output`
Contiene impostazioni relative ai file creati dal programma.

### `files.output.csv`
Percorso (relativo o assoluto) al file `csv` da generare.

> Valore di default
> 
> `./Documenti.csv`
{: .note-title .fs-3 }

## `options.output`
### `options.output.csv_template`
Questa voce definisce il formato di ogni riga del `csv` finale.
> Valore di default
> 
> `"@{CustomerName} {CustomerCode}@{eval_IndirizzoSpedizione} {eval_CAPSpedizione} {eval_CittaSpedizione}(20){eval_intervalloSpedizione}^{eval_pesoSpedizione}^"`
{: .note-title .fs-3 }
