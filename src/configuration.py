# ------------------ CONFIGURAZIONE INPUT ------------------
XML_EASYFATT_FILE   = "./Documenti.DefXml"
""" File `*.DefXML` generato dal gestionale "Danea Easyfatt". """


XML_ADDITIONAL_FILE = "./PRIMARIGA.xml"
""" File `*.xml` con le righe da aggiungere come primo figlio del tag `Documents`. """



# ------------------ CONFIGURAZIONE OUTPUT ------------------
CSV_OUTPUT_FILE     = "./Documenti.csv"
""" Percorso al file CSV di output. """


TEMPLATE_STRING = "@{CustomerName} {CustomerCode}@{eval_IndirizzoSpedizione} {eval_CAPSpedizione} {eval_CittaSpedizione}(20){eval_intervalloSpedizione}^{eval_pesoSpedizione}^"
""" Stringa utilizzata come template per OGNI riga del CSV. NON MODIFICARE I NOMI DEI PLACEHOLDER! """