"""Configurazione della generazione della documentazione con Sphinx.

Il file imposta il percorso di importazione del pacchetto, le estensioni
attive e l'aspetto delle pagine prodotte. Sphinx lo legge automaticamente
all'avvio della generazione e ne applica le impostazioni.
"""

import os
import sys

# Pone la radice della repository sul percorso di ricerca dei moduli.
# L'estensione autodoc importa i moduli del pacchetto per estrarne le
# docstring: senza questa riga il pacchetto ``winery_adventures`` non
# risulterebbe importabile dalla cartella ``docs/`` e la generazione
# fallirebbe. La radice corrisponde alla cartella superiore a ``docs/``.
sys.path.insert(0, os.path.abspath(".."))

# -- Informazioni sul progetto ------------------------------------------------

project = "Winery Adventures"
author = "Luca Bellu, Michele Sciarra"
copyright = "2026, Luca Bellu, Michele Sciarra"
release = "0.1.0"
language = "it"

# -- Estensioni ---------------------------------------------------------------

# autodoc  estrae la documentazione direttamente dalle docstring del codice.
# viewcode aggiunge a ogni oggetto documentato un collegamento al sorgente.
# L'estensione napoleon non compare: interpreta le docstring in stile Google o
# NumPy, mentre quelle del progetto sono già in reStructuredText nativo, che
# autodoc comprende senza intermediari.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
]

# Comportamento predefinito di autodoc per ogni oggetto documentato:
# include i membri pubblici e mostra la classe base da cui derivano le
# sottoclassi, informazione utile a rendere esplicita la gerarchia.
autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
}

# -- Aspetto delle pagine -----------------------------------------------------

# Tema predefinito di Sphinx, privo di dipendenze aggiuntive.
html_theme = "alabaster"